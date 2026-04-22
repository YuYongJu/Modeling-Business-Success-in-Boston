import pandas as pd
import requests
import time

import shared

FOOD_DATA_FILENAME = 'data/food_drink_licenses.csv'
MAPTILER_API_KEY = shared.MAPTILER_API_KEY
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
