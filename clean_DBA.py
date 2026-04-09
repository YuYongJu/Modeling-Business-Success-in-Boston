import pandas as pd

folder = "/Users/tulahionas/Spring_2026_DS_2500/Final_Project/"
filename = "CityofBoston-CityClerkDBA.csv"

df = pd.read_csv(folder + filename, encoding="latin-1")

# Drop unwanted columns
df = df.drop(columns=[
    "Ã¯Â»Â¿File Number",
    "File Number",
    "Owner Name",
    "Owner Address",
    "Owner Email"
])

# Fix garbled zip codes by stripping non-numeric characters
df["Zipcode"] = df["Zipcode"].astype(str).str.replace(r"[^\d]", "", regex=True).str.zfill(5)

# Save cleaned file
df.to_csv(folder + "CityofBoston-CityClerkDBA_cleaned.csv", index=False)

print("Remaining columns:")
print(df.columns.tolist())
