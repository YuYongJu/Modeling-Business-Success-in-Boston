import requests
import pandas as pd
import time
from urllib.parse import quote
import os
import re

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

def handle_withdrawals(df):
    '''
    Withdrawal rows mark either a closure or a re-registration.
    - If a matching business (same name, same address) was filed 
      on or near the withdrawal's expiration date, it's a 
      re-registration: backdate the new entry's filing date.
    - Otherwise it's a closure: transfer the expiration date 
      to the original entry.
    Drop all withdrawal rows after processing.
    '''
    df['Date of Filing'] = pd.to_datetime(df['Date of Filing'], errors='coerce')
    df['Date of Expiration'] = pd.to_datetime(df['Date of Expiration'], errors='coerce')

    withdrawals = df[df['Type of Business'].str.upper() == 'WITHDRAWAL'].copy()
    refile_window = pd.Timedelta(days=30)

    reregistrations = 0
    closures = 0

    for _, w in withdrawals.iterrows():
        match = (
            (df['Business Name'] == w['Business Name']) &
            (df['Business Address'] == w['Business Address']) &
            (df['Type of Business'].str.upper() != 'WITHDRAWAL')
        )
        same_day = (
            match &
            ((df['Date of Filing'] - w['Date of Expiration']).abs() <= refile_window)
        )
        if same_day.any():
            df.loc[same_day, 'Date of Filing'] = w['Date of Filing']
            reregistrations += 1
        else:
            # actual closure — transfer expiration date
            if match.any():
                df.loc[match, 'Date of Expiration'] = w['Date of Expiration']
            closures += 1

    before = len(df)
    df = df[df['Type of Business'].str.upper() != 'WITHDRAWAL'].reset_index(drop=True)
    print(f"Removed {before - len(df)} withdrawal rows "
          f"({reregistrations} re-registrations backdated, "
          f"{closures} closures transferred).")
    return df

def classify_withdrawal(w):
    w = w.strip()
    if w.upper() == 'WITHDRAWAL':
        return 'plain'
    elif re.search(r'\(\d+/\d+/\d+\)', w):
        return 'references date'
    else:
        return 'other'

def extract_referenced_date(w):
    match = re.search(r'\((\d+/\d+/\d+)\)', w)
    return pd.to_datetime(match.group(1), errors='coerce') if match else pd.NaT


def main():
    df = pd.read_csv(folder + filename, encoding="latin-1", dtype={"Zipcode": str})
    df["Zipcode"] = df["Zipcode"].str.encode("ascii", errors="ignore").str.decode("ascii").str.strip()

    clear_private_info(df, [["File Number", "Owner Name", "Owner Address", "Owner Email", 'Ã¯Â»Â¿File Number']])
    df = drop_missing_addresses(df)

    cleaned_path = folder + "CityofBoston-CityClerkDBA_cleaned.csv"
    if os.path.exists(cleaned_path):
        df = pd.read_csv(cleaned_path)
    else:
        df = geocode_addresses(df)
        df.to_csv(cleaned_path, index=False)

    # also process all businesses with "WITHDRAWL" double entries!! dates line up for renewal.
    # calc age

    withdrawals = df[df['Type of Business'].str.upper().str.startswith('WITHDRAWAL')]
    withdrawals['withdrawal_type'] = withdrawals['Type of Business'].apply(classify_withdrawal)
    date_withdrawals = withdrawals[withdrawals['withdrawal_type'] == 'references date'].copy()
    date_withdrawals['referenced_date'] = date_withdrawals['Type of Business'].apply(extract_referenced_date)
    date_withdrawals['Date of Filing'] = pd.to_datetime(date_withdrawals['Date of Filing'], errors='coerce')
    df['Date of Filing'] = pd.to_datetime(df['Date of Filing'], errors='coerce')

    print(withdrawals['withdrawal_type'].value_counts())
    print(f"\nTotal withdrawals: {len(withdrawals)}")
    continuous = 0
    gap = 0
    for _, w in date_withdrawals.iterrows():
        new_entry = df[
            (df['Business Name'] == w['Business Name']) &
            (df['Business Address'] == w['Business Address']) &
            (~df['Type of Business'].str.upper().str.startswith('WITHDRAWAL'))
        ]
        if new_entry.empty:
            gap += 1
            continue
        diff = abs((w['Date of Filing'] - new_entry['Date of Filing'].iloc[0]).days)
        if diff <= 30:
            continuous += 1
        else:
            gap += 1

    print(f"Continuous (<=30 days): {continuous}")
    print(f"Gap (>30 days): {gap}")

    #df.to_csv(folder + "CityofBoston-CityClerkDBA_cleaned.csv", index=False)

    '''
    get_lat_lon(df["Business Address"], df["City"], df["State"], df["Zipcode"])
    df = add_lat_lon(df)
    '''


if __name__ == "__main__":
    main()

