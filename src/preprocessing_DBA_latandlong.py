import requests
import pandas as pd

folder = "data/"
filename = "CityofBoston-CityClerkDBA.csv"

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

def main():
    df = pd.read_csv(folder + filename, encoding="latin-1", dtype={"Zipcode": str})
    df["Zipcode"] = df["Zipcode"].str.encode("ascii", errors="ignore").str.decode("ascii").str.strip()
    print(df.columns)

    # Clear private information
    try:
        for col in ["File Number", "Owner Name", "Owner Address", "Owner Email"]:
            df.drop(columns = col, inplace=True)
    
    except KeyError:
        print("Some columns to drop were not found.")

    #df = drop_missing_coordinates(df)
    df.to_csv(folder + "CityofBoston-CityClerkDBA_cleaned.csv", index=False)

    #print(df[["Business Address", "City", "Zipcode", "Latitude", "Longitude"]].head())
    print(df.head())
    

    '''
    get_lat_lon(df["Business Address"], df["City"], df["State"], df["Zipcode"])
    df = add_lat_lon(df)
    '''


if __name__ == "__main__":
    main()

