# Take the data from the API and csv and add distance from train stop
import fetch_mbtaAPI
import fetch_foodanddrink
from math import sqrt

# For each business, compare their gps location to gps location of train stops

MAPTILER_API_KEY = 'aufX5kxfegadK9an5cZU'
BATCH_SIZE = 50

def calculate_distance(gps1, gps2):
    '''
    Calculate distance between two gps coordinates.
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

def transform_batch(coords):
    """
    coords: list of (gpsx, gpsy) tuples
    Returns list of (lat, lon) tuples
    """
    coord_str = ";".join(f"{x},{y}" for x, y in coords)
    url = f"https://api.maptiler.com/coordinates/transform/{coord_str}.json"
    params = {
        "s_srs": 2249,
        "t_srs": 4326,
        "key": MAPTILER_API_KEY,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    results = response.json()["results"]
    return [(r["y"], r["x"]) for r in results]  # (lat, lon)

def transform_all(df, x_col="gpsx", y_col="gpsy"):
    """
    Transform all rows in a DataFrame from EPSG:2249 to lat/lon.
    Adds 'latitude' and 'longitude' columns.
    """
    coords = list(zip(df[x_col], df[y_col]))
    transformed_coords = []
    
    for i in range(0, len(coords), BATCH_SIZE):
        batch = coords[i:i + BATCH_SIZE]
        transformed_batch = transform_batch(batch)
        transformed





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

def main():
    stops_df = fetch_mbtaAPI.main()
    businesses_df = fetch_foodanddrink.main()
    print(stops_df.head(10))
    print(businesses_df.head(10))
    print("Food and drink data loaded.")
    df = add_distance_to_stops(businesses_df, stops_df)
    print(df.head(10))

if __name__ == '__main__':
    main()