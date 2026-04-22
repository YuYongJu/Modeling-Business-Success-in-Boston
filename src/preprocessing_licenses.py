import pandas as pd
import requests
import time
import os

import shared

FOLDER = "data/"
FILENAME = "food_drink_licenses"

ORIGINAL_PATH = f"{FOLDER}{FILENAME}.csv"
CLEANED_PATH = f"{FOLDER}{FILENAME}_cleaned.csv"
MAPTILER_API_KEY = '0hnVPQyYgsNAoCUxs2lH'
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
    Attributes: DataFrame with 'gpsx' and 'gpsy' columns
    Returns: DataFrame with 'latitude' and 'longitude' columns added, 
                        and original 'gpsx' and 'gpsy' columns removed.
    """
    coords = list(zip(df[x_col], df[y_col]))
    transformed_coords = []

    for i in range(0, len(coords), BATCH_SIZE):
        batch = coords[i:i+BATCH_SIZE]
        transformed_coords.extend(transform_EPSG_GPS(batch))

    print("transformed coords:", len(transformed_coords))
    df["latitude"] = [lat for lat, lon in transformed_coords]  # ← was broken .assign(..., inplace=True)
    df["longitude"] = [lon for lat, lon in transformed_coords]
    df = df.drop(columns=[x_col, y_col])
    return df

def main():
    stops_df = shared.fetch_mbtaAPI()
    try:
        df = pd.read_csv(CLEANED_PATH)
    except FileNotFoundError:
        df = pd.read_csv(ORIGINAL_PATH)
    
    if "latitude" not in df.columns:
        df = df.dropna(subset=["gpsx", "gpsy"])
        df = transform_all_EPSG_GPS(df)

    if 'distance_to_closest_stop' not in df.columns:
        df = shared.add_distance_to_stops(df, stops_df)

    df = shared.normalize_name(df, "dba_name")
    df = shared.find_remove_outliers(df)
    df = shared.encode_neighborhoods(df, 'zip')
    df = shared.calc_age(df, filing_col="issued", expiration_col="expires")
    df.drop(df[df['age_years'] < 0].index, inplace=True)
    df["chain_count"] = df.groupby("business_name_normalized")["business_name_normalized"].transform("count")

    df.to_csv(CLEANED_PATH, index=False)

if __name__ == '__main__':
    main()