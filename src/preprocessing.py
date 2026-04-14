'''
Calculate the following:

business age (float): (today - date of issue) or (prior expiration - date of issue)
business active (boolean)

distance to nearest train stop (float)
nearest train stop (string)

chain/multi-location (int): number of restaurants with matching name
'''

import fetch_mbtaAPI
import fetch_foodanddrink
import preprocessing_DBA_latandlong

import requests
import matplotlib.pyplot as plt
from math import sqrt
import time # for a pause between API calls to avoid rate limits
import shared

save_location = 'eda_plots/'

# For each business, compare their gps location to gps location of train stops

BATCH_SIZE = 50

def drop_missing_coords(df, x_col="gpsx", y_col="gpsy"):
    """
    Remove rows with missing GPS coordinates.
    """
    before = len(df)
    df = df.dropna(subset=[x_col, y_col], inplace=True)
    after = len(df)
    print(f"Removed {before - after} rows with missing coordinates ({after} remaining)")

def transform_EPSG_GPS(coords):
    """
    Attributes:
        coords: list of (gpsx, gpsy) tuples in EPSG:2249
            (Massachusetts State Plane NAD83, US Survey Feet)
    Returns:
        list of (lat, lon) tuples in EPSG:4326
    """
    coord_str = ";".join(f"{x},{y}" for x, y in coords)
    url = f"https://api.maptiler.com/coordinates/transform/{coord_str}.json"
    params = {
        "s_srs": 2249,  # MA State Plane NAD83, US Survey Feet
        "t_srs": 4326,  # WGS84 — standard GPS lat/lon
        "key": MAPTILER_API_KEY,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    results = response.json()["results"]
    return [(r["y"], r["x"]) for r in results]  # (lat, lon)

def transform_all_EPSG_GPS(df, x_col="gpsx", y_col="gpsy"):
    """
    Transform gpsx and gpsy columns in the DataFrame from EPSG:2249 to lat/lon in batches of 50 limit.
    Adds 'latitude' and 'longitude' columns.
    Removes original misleading gpsx and gpsy columns.
    """
    coords = list(zip(df[x_col], df[y_col]))
    transformed_coords = []

    for i in range(0, len(coords), BATCH_SIZE):
        batch = coords[i:i+BATCH_SIZE]
        transformed_batch = transform_batch(batch)
        transformed_coords.extend(transformed_batch)

    print("transformed coords:", len(transformed_coords))
    df.assign(latitude=[lat for lat, lon in transformed_coords], longitude=[lon for lat, lon in transformed_coords], inplace=True)

def geocode_addresses(addresses):
    """
    Attributes:
        addresses: list of address strings
    Returns:
        list of (lat, lon) tuples
    """
    results = []
    for address in addresses:
        url = f"https://api.maptiler.com/geocoding/{requests.utils.quote(address)}.json"
        params = {
            "key": MAPTILER_API_KEY,
            "limit": 1,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        features = response.json().get("features", [])
        if features:
            lon, lat = features[0]["geometry"]["coordinates"]
            results.append((lat, lon))
        else:
            results.append((None, None))
    return results


def geocode_all_addresses(df, address_col="Business Address"):
    """
    Geocode all addresses in a DataFrame column in batches of BATCH_SIZE.
    Adds 'latitude' and 'longitude' columns.
    """
    addresses = df[address_col].tolist()
    geocoded = []

    for i in range(0, len(addresses), BATCH_SIZE):
        batch = addresses[i:i+BATCH_SIZE]
        geocoded_batch = geocode_batch(batch)
        geocoded.extend(geocoded_batch)
        time.sleep(1)

    print("geocoded addresses:", len(geocoded))
    df["latitude"] = [lat for lat, lon in geocoded]
    df["longitude"] = [lon for lat, lon in geocoded]
    return df

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
    Calculate age and active status for each business.
    Attributes: dataframe
    Returns: dataframe with two new columns:
        is_active: True if expiration date is in the future.
        age_years: for active businesses, today - date of filing.
                for closed businesses, date of expiration - date of filing.
    '''
    today = pd.Timestamp.today()
    df["Date of Filing"] = pd.to_datetime(df["Date of Filing"], errors="coerce", format="mixed")
    df['Date of Expiration'] = pd.to_datetime(df['Date of Expiration'], errors='coerce', format="mixed")
    df["issued"] = pd.to_datetime(df.get("issued"), errors="coerce")

    df['is_active'] = df['Date of Expiration'] > today
    end_date = df['Date of Expiration'].where(~df['is_active'], other=today)
    df['age_years'] = (end_date - df['Date of Filing']).dt.days / 365
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
        Distance in meters between the two locations
    '''
    lat1, lon1 = gps1
    lat2, lon2 = gps2

    distance = ((lat1 - lat2) + (lon1 - lon2)) * 111111  # Approximate conversion to kilometers

    return distance

def add_distance_to_stops(businesses_df, stops_df):
    '''
    For each business, calculate distance to each train stop and add the shortest distance and the name of the closest stop to the dataframe.
    Attributes:
        businesses_df: DataFrame containing business information including 'latitude' and 'longitude' columns
        stops_df: DataFrame containing train stop information including 'latitude' and 'longitude' columns
    Returns:
        Updated businesses_df with new columns 'closest_stop' and 'distance_to_closest_stop'
    '''
    for index, business in businesses_df.iterrows():
        min_distance = float('inf')
        closest_stop = None
        for _, stop in stops_df.iterrows():
            distance = calculate_distance((business['gpsx'], business['gpsy']), (stop['latitude'], stop['longitude']))
            if distance < min_distance:
                min_distance = distance
                closest_stop = stop['name']
        businesses_df.at[index, 'closest_stop'] = closest_stop
        businesses_df.at[index, 'distance_to_closest_stop'] = min_distance

    return businesses_df

def find_remove_outliers(df):
    before = len(df)
    df = df[
        (df["latitude"] >= 41) & (df["latitude"] <= 43) &
        (df["longitude"] >= -72) & (df["longitude"] <= -70)
    ]
    after = len(df)
    print(f"Removed {before - after} outliers based on latitude and longitude ({after} remaining)")
    return df


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
    #fetch all data
    stops_df = fetch_mbtaAPI.main()
    try:
        df = pd.read_csv('data/compiled_data.csv')
    except:
        df = pd.read_csv('data/CityofBoston-CityClerkDBA_cleaned.csv')

    if 'distance_to_closest_stop' in df.columns:
        pass
    else:
        df = add_distance_to_stops(df, stops_df)

    df = shared.normalize_name(df, "Business Name")
    df = find_remove_outliers(df)
    df = shared.encode_neighborhoods(df, 'Zipcode')
    df = calc_age(df)
    df.drop(df[df['age_years'] < 0].index, inplace=True)
    df = add_chain_count(df)

    df.to_csv("data/compiled_data.csv", index=False)

if __name__ == '__main__':
    main()
