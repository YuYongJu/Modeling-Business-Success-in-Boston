# Take the data from the API and csv and add distance from train stop
import fetch_mbtaAPI
import fetch_foodanddrink
import requests
import matplotlib.pyplot as plt
from math import sqrt

# For each business, compare their gps location to gps location of train stops

MAPTILER_API_KEY = 'aufX5kxfegadK9an5cZU'
BATCH_SIZE = 50

def drop_missing_coords(df, x_col="gpsx", y_col="gpsy"):
    """
    Remove rows with missing GPS coordinates.
    """
    before = len(df)
    df = df.dropna(subset=[x_col, y_col])
    after = len(df)
    print(f"Removed {before - after} rows with missing coordinates ({after} remaining)")
    return df

def transform_batch(coords):
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

def transform_all(df, x_col="gpsx", y_col="gpsy"):
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
    return df.assign(latitude=[lat for lat, lon in transformed_coords], longitude=[lon for lat, lon in transformed_coords])

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

    lat_diff = lat1 - lat2
    lon_diff = lon1 - lon2

    distance = sqrt(lat_diff**2 + lon_diff**2) * 111111  # Approximate conversion to kilometers

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

outliers = transformed_businesses_df[
    (transformed_businesses_df["latitude"] < 41) |
    (transformed_businesses_df["latitude"] > 43) |
    (transformed_businesses_df["longitude"] < -72) |
    (transformed_businesses_df["longitude"] > -70)
]
print(outliers[["latitude", "longitude", "gpsx", "gpsy"]])

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
    plt.savefig("boston_map.png", dpi=150)
    plt.show()

def main():
    stops_df = fetch_mbtaAPI.main()
    businesses_df = fetch_foodanddrink.main()
    print("Food and drink data loaded.")
    businesses_df = drop_missing_coords(businesses_df)
    transformed_businesses_df = transform_all(businesses_df)
    print(transformed_businesses_df.head(10))
    businesses_df = add_distance_to_stops(businesses_df, stops_df)
    plot_coords(transformed_businesses_df, stops_df)

if __name__ == '__main__':
    main()