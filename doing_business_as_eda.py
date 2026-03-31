# doing business as database eda
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dba = pd.read_csv('/Users/abigailrillovick/Desktop/26s-ds2500-rillovick/project/CityofBoston-DBA_cleaned.csv')

# classify active vs. expired
dba['Date of Expiration'] = pd.to_datetime(dba['Date of Expiration'], errors='coerce')
dba['Date of Filing'] = pd.to_datetime(dba['Date of Filing'], errors='coerce')
today = pd.Timestamp.today()
dba['is_active'] = (dba['Date of Expiration'] > today)

# map data to neighborhood, same as food/drink licenses zips
ZIPS_BY_NEIGHBORHOOD = {
    'Allston/Brighton': [2134, 2135, 2163],
    'Back Bay/Beacon Hill': [2108, 2116, 2117, 2123, 2133, 2199, 2216, 2217, 2295],
    'Central Boston': [2101, 2102, 2103, 2104, 2105, 2106, 2107, 2109, 2110, 2111, 2112, 2113, 2114, 2196, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2211, 2212, 2222, 2293],
    'Charlestown': [2129],
    'Dorchester': [2122, 2124, 2125],
    'East Boston': [2128, 2228],
    'Fenway/Kenmore': [2115, 2215],
    'Hyde Park': [2136],
    'Jamaica Plain': [2130],
    'Mattapan': [2126],
    'Roslindale': [2131],
    'Roxbury': [2119, 2120, 2121],
    'South Boston': [2127],
    'Seaport': [2210],
    'South End': [2118],
    'West Roxbury': [2132]
}

zip_to_neighborhood = {z: n for n, zips in ZIPS_BY_NEIGHBORHOOD.items() for z in zips}
dba['neighborhood'] = dba['Zipcode'].map(zip_to_neighborhood)
dba = dba.dropna(subset=['neighborhood'])

# chart 1: overall active vs. expired businesses
dba['is_active'].value_counts().plot(kind='bar', figsize=(6,4), color=['steelblue', 'orange'],
                                     title='Active vs. Expired Businesses (Overall)')
plt.xticks([0,1], ['Active', 'Expired'], rotation=0)
plt.ylabel('Counts')
plt.tight_layout()
plt.savefig('dba_active_expired_overall.png')
plt.show()

# CONCLUSION: ~2600 active vs ~1200 expired businesses
# roughly 68% of businesses still active in this dataset

# chart 2: active rate by neighborhood
active_by_neighborhood = dba.groupby(['neighborhood', 'is_active']).size().unstack(fill_value=0)
active_by_neighborhood.columns = ['Expired', 'Active']
active_by_neighborhood['pct_active'] = (
    active_by_neighborhood['Active'] /
    (active_by_neighborhood['Active'] + active_by_neighborhood['Expired']) * 100
)
active_by_neighborhood['pct_active'].sort_values().plot(
    kind='bar', figsize=(12,5), color='steelblue',
    title='% of Active Businesses by Neighborhood')
plt.xlabel('Neighborhood')
plt.ylabel('% Active')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('dba_pct_active_by_neighborhood.png')
plt.show()

# CONCLUSION: only 4 neighborhoods (others had too few businesses to analyze). 
# Back Bay/Beacon Hill has highest active rate (~71%)
# Fenway/Kenmore is second (~70%)
# South Boston and Roxbury are slightly lower (~65%)
# Fenway/Kenmore having higher active rate suggests businesses there are doing well.
# Back Bay/Beacon Hill has wealthier, higher-foot traffic areas, which aligns with results here. 

print("\n Active business counts by neighborhood: ")
print(active_by_neighborhood['pct_active'].sort_values(ascending=False).round(1))