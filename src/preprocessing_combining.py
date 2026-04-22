'''
Calculate the following:

business age (float): (today - date of issue) or (prior expiration - date of issue)
business active (boolean)

distance to nearest train stop (float)
nearest train stop (string)

chain/multi-location (int): number of restaurants with matching name
'''
import pandas as pd
import requests
from math import sqrt
import time # for a pause between API calls to avoid rate limits

import fetch_foodanddrink
import preprocessing_DBA_latandlong
import shared

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
            dist = shared.calculate_distance(
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
        dist = shared.calculate_distance(
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
    stops_df = shared.fetch_mbtaAPI()
    try:
        df = pd.read_csv('data/compiled_data.csv')
    except:
        df = pd.read_csv('data/CityofBoston-CityClerkDBA_cleaned.csv')

    if 'distance_to_closest_stop' in df.columns:
        pass
    else:
        df = shared.add_distance_to_stops(df, stops_df)

    df = shared.normalize_name(df, "Business Name")
    df = shared.find_remove_outliers(df)
    df = shared.encode_neighborhoods(df, 'Zipcode')
    df = shared.calc_age(df, filing_col="issued", expiration_col="expires")
    df.drop(df[df['age_years'] < 0].index, inplace=True)
    df["chain_count"] = df.groupby(name_col)[name_col].transform("count")

    df.to_csv("data/compiled_data.csv", index=False)

if __name__ == '__main__':
    main()
