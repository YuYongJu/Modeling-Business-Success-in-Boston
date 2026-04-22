import requests
import pandas as pd
import time
from urllib.parse import quote

MAPTILER_API_KEY = '0hnVPQyYgsNAoCUxs2lH'

folder = "data/"
filename = "CityofBoston-CityClerkDBA"

def clear_private_info(df):
    '''
    Clear private information from the DataFrame.
    '''
    cols_to_drop = ["File Number", "Owner Name", "Owner Address", "Owner Email"]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)


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
    df["Latitude"], df["Longitude"] = zip(*df.apply(
        lambda row: get_lat_lon(row["Business Address"], row["City"], row["State"], row["Zipcode"]),
        axis=1
    ))
    return df

def drop_missing_coordinates(df):
    '''
    Drop rows where Latitude or Longitude is missing
    '''
    before = len(df)
    df.dropna(subset=["Latitude", "Longitude"], inplace=True)
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
    """
    Geocodes a single address using the Census geolocator. 
    """
    geolocator = Census(user_agent="boston_business_longevity")
    try:
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
    """
    Geocodes a single address using the Maptiler Geocoding API.
    Cleans the address by removing unit numbers and extra details. 
    """
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
    Attributes:
        df: DataFrame containing the addresses to geocode
        address_col: name of the column containing the address strings
    Returns:
        dataframe with 'latitude' and 'longitude' columns added
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

def handle_withdrawals(df, gap_threshold=30):
    '''
    Processes withdrawal entries in the DBA dataset.
    Attributes:
        dataframe
        threshold of days between withdraw and other business entry filing
    Methods:
        If "withdraw" business is continuous or re-filed within the threshold, consider continuous.
            revise non-"withdraw" business entry with the earliest start date and latest end date.
        Else consider it a closure, and two separate businesses.
            set expiration date ("end date") to withdraw date
    Returns:
        dataframe with revised business entries, and dropped withdraw rows.
    '''
    df['Date of Filing'] = pd.to_datetime(df['Date of Filing'], errors='coerce', format="mixed")
    df['Date of Expiration'] = pd.to_datetime(df['Date of Expiration'], errors='coerce', format="mixed")

    is_withdrawal = df['Type of Business'].str.upper().str.startswith('WITHDRAWAL', na=False)
    date_withdrawals = df[
        is_withdrawal &
        df['Type of Business'].str.contains(r'\(\d+/\d+/\d+\)', regex=True, na=False)
    ].copy()

    continuous = 0
    closures = 0

    for _, w in date_withdrawals.iterrows():
        match = (
            (df['Business Name'] == w['Business Name']) &
            (df['Business Address'] == w['Business Address']) &
            (~df['Type of Business'].str.upper().str.startswith('WITHDRAWAL', na=False))
        )
        if not match.any():
            continue

        original = df[match].iloc[0]
        diff = abs((w['Date of Filing'] - original['Date of Filing']).days)

        if diff <= gap_threshold:
            df.loc[match, 'Date of Filing'] = original['Date of Filing']
            continuous += 1
        else:
            df.loc[match, 'Date of Expiration'] = w['Date of Filing']
            closures += 1

    before = len(df)
    df = df[~is_withdrawal].reset_index(drop=True)
    print(f"Removed {before - len(df)} withdrawal rows "
          f"({continuous} re-registrations backdated, "
          f"{closures} closures transferred).")
    return df

def main():
    try:
        cleaned_path = folder + filename + '_cleaned.csv'
        df = pd.read_csv(cleaned_path, encoding="latin-1", dtype={"Zipcode": str})
    except:
        path = folder + filename + '.csv'
        df = pd.read_csv(path, encoding="latin-1", dtype={"Zipcode": str})
        df["Zipcode"] = df["Zipcode"].str.encode("ascii", errors="ignore").str.decode("ascii").str.strip()

    clear_private_info(df)
    df = drop_missing_addresses(df)
    df = handle_withdrawals(df)

    if 'latitude' in df.columns and 'longitude' in df.columns:
        pass
    else:
        df = geocode_addresses(df)

    print(df.columns)

    cleaned_path = folder + filename + '_cleaned.csv'
    df.head(1000).to_csv(cleaned_path, index=False)


if __name__ == "__main__":
    main()
