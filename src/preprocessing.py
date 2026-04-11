# Take the data from the API and csv and add distance from train stop
import fetch_mbtaAPI
import fetch_foodanddrink
import preprocessing_DBA_latandlong
import pandas as pd
import requests
import matplotlib.pyplot as plt
from math import sqrt

def compile_datasets(df1, df2):
    '''
    Combine the two business dataframes, adding any missing columns to each and filling with NaN.
    '''
    rename_map = {
        "Business Name": "business_name",
        "Business Address": "address",
        "Type of Business": "license_category",
        "City": "city",
        "State": "state",
        "Zipcode": "zip",
    }
    df2 = df2.rename(columns=rename_map)
    combined = pd.concat([df1, df2], ignore_index=True)
    combined["business_name_normalized"] = combined["business_name"].apply(
        lambda name: ''.join(char for char in str(name).lower() if char.isalnum() or char.isspace())
        .replace("inc", "").replace("llc", "").strip())
    combined = combined.drop_duplicates(subset=["business_name_normalized", "latitude", "longitude"])
    combined = fuzzy_duplicates(combined, name_col="business_name")
    print("combined:", len(combined))

    return combined

def calc_age(df):
    '''
    Calculate age from today - date of issue
    '''
    today = pd.Timestamp.today()
    df["Date of Filing"] = pd.to_datetime(df.get("Date of Filing"), errors="coerce", format="mixed")
    df["issued"] = pd.to_datetime(df.get("issued"), errors="coerce")
    
    df["age_years"] = (today - df["Date of Filing"]).dt.days / 365
    missing = df["age_years"].isna()
    df.loc[missing, "age_years"] = (today - df.loc[missing, "issued"]).dt.days / 365
    print(f"No age: {df['age_years'].isna().sum()} businesses")
    return df

def add_chain_count(df, name_col="business_name_normalized"):
    df["chain_count"] = df.groupby(name_col)[name_col].transform("count")
    return df

def calculate_distance(gps1, gps2):
    '''
    Calculate Manhattan distance (city blocks) between two gps coordinates.
    Attributes:
        gps1: tuple of (latitude, longitude) for first location
        gps2: tuple of (latitude, longitude) for second location
    Returns:
        Distance in kilometers between the two locations
    '''
    lat1, lon1 = gps1
    lat2, lon2 = gps2

    distance = (abs(lat1 - lat2) + abs(lon1 - lon2)) * 111111  # Approximate conversion to kilometers

    return distance

def add_distance_to_stops(df, stops_df):
    '''
    For each business, calculate distance to each train stop and add the shortest distance and the name of the closest stop to the dataframe.
    Attributes:
        businesses_df: DataFrame containing business information including 'latitude' and 'longitude' columns
        stops_df: DataFrame containing train stop information including 'latitude' and 'longitude' columns
    Returns:
        Updated businesses_df with new columns 'closest_stop' and 'distance_to_closest_stop'
    '''
    for index, business in df.iterrows():
        min_distance = float('inf')
        closest_stop = None
        for _, stop in stops_df.iterrows():
            distance = calculate_distance((business['latitude'], business['longitude']), (stop['latitude'], stop['longitude']))
            if distance < min_distance:
                min_distance = distance
                closest_stop = stop['name']
        df.at[index, 'closest_stop'] = closest_stop
        df.at[index, 'distance_to_closest_stop'] = min_distance

    return df

def find_remove_outliers(df):
    before = len(df)
    df = df[
        (df["latitude"] >= 41) & (df["latitude"] <= 43) &
        (df["longitude"] >= -72) & (df["longitude"] <= -70)
    ]
    after = len(df)
    print(f"Removed {before - after} outliers based on latitude and longitude ({after} remaining)")
    return df

def plot_coords(businesses_df, stops_df):
    """
    Plot business and MBTA stop locations.
    Businesses in blue, stops in red.
    """
    plt.figure(figsize=(10, 10))

    plt.scatter(
        businesses_df["longitude"], businesses_df["latitude"],
        c="blue", s=5, alpha=0.5, label="Businesses"
    )
    plt.scatter(
        stops_df["longitude"], stops_df["latitude"],
        c="red", s=20, alpha=0.8, label="MBTA Stops"
    )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Boston Businesses and MBTA Stops")
    plt.legend()
    plt.tight_layout()
    plt.xlim(-71.2, -70.9)
    plt.ylim(42.2, 42.4)
    plt.savefig("boston_map.png", dpi=150)
    plt.show()

from difflib import SequenceMatcher

DISTANCE_THRESHOLD_KM = 0.15
NAME_SIMILARITY_THRESHOLD = 0.85  # 0–1, higher = stricter matching

def fuzzy_duplicates(df, name_col="business_name"):
    """
    Removes duplicate businesses with matching normalized names within DISTANCE_THRESHOLD_KM.
    Keeps the first occurrence.
    """
    df = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
    df = df.sort_values("latitude").reset_index(drop=True)
    rows = df.to_dict("records")
    duplicate_indices = set()

    for i in range(len(rows)):
        if i in duplicate_indices:
            continue
        for j in range(i + 1, len(rows)):
            if j in duplicate_indices:
                continue
            if abs(rows[j]["latitude"] - rows[i]["latitude"]) > 0.0015:
                break
            if rows[i][name_col] != rows[j][name_col]:
                continue
            dist = calculate_distance(
                (rows[i]["latitude"], rows[i]["longitude"]),
                (rows[j]["latitude"], rows[j]["longitude"])
            )
            if dist <= DISTANCE_THRESHOLD_KM:
                duplicate_indices.add(j)

    before = len(df)
    df = df.drop(index=list(duplicate_indices)).reset_index(drop=True)
    print(f"Removed {before - len(df)} fuzzy duplicates. {len(df)} remaining.")
    return df

def find_nearby_duplicates(df1, df2, name_col="business_name"):
    """
    Finds businesses in df1 that have a matching name and nearby location in df2.
    """
    rows1 = df1.dropna(subset=["latitude", "longitude"]).to_dict("records")
    rows2 = df2.dropna(subset=["latitude", "longitude"]).to_dict("records")

    for r1 in rows1:
        for r2 in rows2:
            if r1 is r2:
                continue
            if r1[name_col] != r2[name_col]:
                continue
            dist = calculate_distance(
                (r1["latitude"], r1["longitude"]),
                (r2["latitude"], r2["longitude"])
            )
            if dist <= DISTANCE_THRESHOLD_KM:
                pass
                #print(f"{r1[name_col]!r} <--> {r2[name_col]!r} ({dist:.3f} km)")

def _name_similarity(a, b):
    """Returns similarity ratio 0–1 between two strings."""
    return SequenceMatcher(None, str(a).lower().strip(), str(b).lower().strip()).ratio()
 
def merge_similar(df, name_col="business_name"):
    """
    Removes fuzzy duplicate businesses within DISTANCE_THRESHOLD_KM.
    Keeps the first occurrence.
    """
    df = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
    rows = df.to_dict("records")
    duplicate_indices = set()

    for j in range(i + 1, len(rows)):
        if j in duplicate_indices:
            continue
        dist = calculate_distance(
            (rows[i]["latitude"], rows[i]["longitude"]),
            (rows[j]["latitude"], rows[j]["longitude"])
        )
        if dist > DISTANCE_THRESHOLD_KM:
            continue
        if _name_similarity(rows[i][name_col], rows[j][name_col]) < NAME_SIMILARITY_THRESHOLD:
            continue
        duplicate_indices.add(j)

    before = len(df)
    df = df.drop(index=list(duplicate_indices)).reset_index(drop=True)
    print(f"Removed {before - len(df)} fuzzy duplicates. {len(df)} remaining.")
    return df

def main():
    '''
    Fetch data
        - MBTA Stops
        - DBA
        - licenses
    Compile
        - Get rid of repeat businesses (similar name, similar coords)
        - Rename column names
    Calculate
        - Years in Business
        - Distance to train stop + nearest stop
        - (Chain/multi location vs non-chain) # businesses of the same name
    '''

    # FETCH DATA
    #stops_df = fetch_mbtaAPI.main()
    stops_df = pd.read_csv('data/MBTA_stops.csv')
    licenses_df = fetch_foodanddrink.main()
    DBA_df = pd.read_csv('data/CityofBoston-CityClerkDBA_cleaned.csv')
    print("Data Loaded")
    before = len(licenses_df) + len(DBA_df)

    # COMPILE DATA
    df = compile_datasets(licenses_df, DBA_df)
    print(len(df))

    # CALCULATE VARIABLES
    df = calc_age(df)
    df = add_distance_to_stops(df, stops_df)
    print(df.columns)

    # SAVE AS NEW CSV
    #df.to_csv("data/compiled_data.csv", index=False)

    # PLOTS
    df = df[
        (df["latitude"] >= 42.2) & (df["latitude"] <= 42.4) &
        (df["longitude"] >= -71.2) & (df["longitude"] <= -70.9)
    ]
    
    plot_coords(DBA_df, stops_df)

if __name__ == '__main__':
    main()