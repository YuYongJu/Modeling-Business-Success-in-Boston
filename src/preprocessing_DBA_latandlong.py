import requests
import pandas as pd
import time
from urllib.parse import quote

MAPTILER_API_KEY = 'aufX5kxfegadK9an5cZU'

folder = "data/"
filename = "CityofBoston-CityClerkDBA.csv"

def clear_private_info(df, columns_to_drop):
    '''
    Drop columns containing private information.
    '''
    try:
        for col in columns_to_drop:
            df.drop(columns = col, inplace=True)
    except KeyError:
        print("Some columns to drop were not found.")

def get_lat_lon(address, city, state, zipcode):
    '''
    Get latitude and longitude for a given address.
    '''
    try:
        url = "https://geocoding.geo.census.gov/geocoder/locations/address"
        params = {
            "street": address,
            "city": city,
            "state": state,
            "zip": zipcode,
            "benchmark": "Public_AR_Current",
            "format": "json"
        }
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        matches = result["result"]["addressMatches"]
        if matches:
            coords = matches[0]["coordinates"]
            return coords["y"], coords["x"]  # latitude, longitude
        return None, None
    except:
        return None, None

def add_lat_lon(df):
    '''
    Apply get_lat_lon to each row of the DataFrame and add Latitude & Longitude columns.
    '''
    df["latitude"], df["longitude"] = zip(*df.apply(
        lambda row: get_lat_lon(row["Business Address"], row["City"], row["State"], row["Zipcode"]),
        axis=1
    ))
    return df

def drop_missing_coordinates(df):
    '''
    Drop rows where Latitude or Longitude is missing
    '''
    before = len(df)
    df.dropna(subset=["latitude", "longitude"], inplace=True)
    after = len(df)
    print(f"{after}/{before} rows kept. {before - after} rows removed due to missing coordinates.")

def drop_missing_addresses(df, address_col="Business Address"):
    """
    Specifically for the DBA dataset.
    Removes rows where the address string is missing or empty.
    """
    before = len(df)
    df.dropna(subset=[address_col], inplace=True)
    df = df[df[address_col].str.strip() != ""]
    after = len(df)
    return df

def census_geocode(address):
    geolocator = Census(user_agent="boston_business_longevity")
    try:
        # The Census Geocoder is optimized for US addresses
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    return None, None

def geocode_addresses(df):
    """
    Geocodes unique addresses only and maps them back to the DataFrame.
    """
    # Create a unique list of address strings to geocode
    # We combine them into a tuple to ensure we are looking for specific address+zip combos
    unique_rows = df[["Business Address", "Zipcode"]].drop_duplicates()
    address_map = {}
    
    total_unique = len(unique_rows)
    print(f"Geocoding {total_unique} unique locations...")

    for i, (_, row) in enumerate(unique_rows.iterrows()):
        if i % 10 == 0:
            print(f"Progress: {i}/{total_unique} ({(i/total_unique)*100:.1f}%)")
            
        lat, lon = maptiler_geocode(row["Business Address"], row["Zipcode"])

        address_key = f"{row['Business Address']}, {row['Zipcode']}"
        address_map[address_key] = (lat, lon)
        
        time.sleep(0.1)
    
    def get_from_map(row):
        key = f"{row['Business Address']}, {row['Zipcode']}"
        return address_map.get(key, (None, None))

    df["latitude"], df["longitude"] = zip(*df.apply(get_from_map, axis=1))
    return df

def maptiler_geocode(address, zipcode):
    clean_address = str(address).split(',')[0].split('#')[0].strip()
    full_query = f"{clean_address}, {zipcode}"
    
    url = f"https://api.maptiler.com/geocoding/{requests.utils.quote(full_query)}.json"
    params = {"key": MAPTILER_API_KEY, "limit": 1}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("features"):
                lon, lat = data["features"][0]["geometry"]["coordinates"]
                return lat, lon
    except Exception as e:
        print(f"Error geocoding {clean_address}: {e}")
        
    return None, None

def main():
    df = pd.read_csv(folder + filename, encoding="latin-1", dtype={"Zipcode": str})
    df["Zipcode"] = df["Zipcode"].str.encode("ascii", errors="ignore").str.decode("ascii").str.strip()

    clear_private_info(df, [["File Number", "Owner Name", "Owner Address", "Owner Email", 'Ã¯Â»Â¿File Number']])
    df = drop_missing_addresses(df)
    df = geocode_addresses(df)

    df.to_csv(folder + "CityofBoston-CityClerkDBA_cleaned.csv", index=False)

    '''
    get_lat_lon(df["Business Address"], df["City"], df["State"], df["Zipcode"])
    df = add_lat_lon(df)
    '''


if __name__ == "__main__":
    main()

