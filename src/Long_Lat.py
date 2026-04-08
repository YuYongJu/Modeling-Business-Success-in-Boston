import requests
import pandas as pd

folder = "/Users/tulahionas/Spring_2026_DS_2500/Final_Project/"
filename = "CityofBoston-CityClerkDBA_cleaned.csv"

df = pd.read_csv(folder + filename, dtype={"Zipcode": str})

def get_lat_lon(address, city, state, zipcode):
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
df["Latitude"], df["Longitude"] = zip(*df.apply(
    lambda row: get_lat_lon(row["Business Address"], row["City"], row["State"], row["Zipcode"]),
    axis=1
))

# Save updated file
df.to_csv(folder + "CityofBoston-CityClerkDBA_cleaned.csv", index=False)

# Drop rows where Latitude or Longitude is missing
before = len(df)
df = df.dropna(subset=["Latitude", "Longitude"])
after = len(df)

# Save updated file
df.to_csv(folder + "CityofBoston-CityClerkDBA_cleaned.csv", index=False)

# Summary
print(f"Done! {after}/{before} rows kept. {before - after} rows removed due to missing coordinates.")
print(df[["Business Address", "City", "Zipcode", "Latitude", "Longitude"]].head())



