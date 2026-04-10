import requests
import pandas as pd

folder = "data/"
filename = "CityofBoston-CityClerkDBA_cleaned.csv"


def get_lat_lon(address, city, state, zipcode):
    '''
    Docstring
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

# Apply to each row and add Latitude & Longitude columns
def add_lat_lon(df):
    '''
    Docstring
    '''
    df["Latitude"], df["Longitude"] = zip(*df.apply(
        lambda row: get_lat_lon(row["Business Address"], row["City"], row["State"], row["Zipcode"]),
        axis=1
    ))
    return df

# Drop rows where Latitude or Longitude is missing
def drop_missing_coordinates(df):
    '''
    Docstring
    '''
    before = len(df)
    df = df.dropna(subset=["Latitude", "Longitude"])
    after = len(df)
    print(f"{after}/{before} rows kept. {before - after} rows removed due to missing coordinates.")
    return df

def main():
    df = pd.read_csv(folder + filename, dtype={"Zipcode": str})
    get_lat_lon(df["Business Address"], df["City"], df["State"], df["Zipcode"])
    df = add_lat_lon(df)
    df = drop_missing_coordinates(df)
    df.to_csv(folder + "CityofBoston-CityClerkDBA_cleaned.csv", index=False)
    print(df[["Business Address", "City", "Zipcode", "Latitude", "Longitude"]].head())


if __name__ == "__main__":
    main()

