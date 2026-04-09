import pandas as pd

folder = "/Users/tulahionas/Spring_2026_DS_2500/Final_Project/"

files = [
    "02120 - CityofBoston-CityClerkDBA.csv",
    "02116 - CityofBoston-CityClerkDBA.csv",
    "02115 - CityofBoston-CityClerkDBA.csv",
    "02127 - CityofBoston-CityClerkDBA.csv",
    "02108 - CityofBoston-CityClerkDBA.csv"
]

df = pd.concat([pd.read_csv(folder + f, encoding="latin-1") for f in files], ignore_index=True)
df.to_csv("CityofBoston-CityClerkDBA.csv", index=False)
