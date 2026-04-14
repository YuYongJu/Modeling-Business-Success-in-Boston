# Alcohol License Analysis

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ZIPS_BY_NEIGHBORHOOD = {
        'Allston/Brighton' : [2134, 2135, 2163],
        'Back Bay/Beacon Hill ' : [2108, 2116, 2117, 2123, 2133, 2199, 2216, 2217, 2295],
        'Central Boston' : [2101, 2102, 2103, 2104, 2105, 2106, 2107, 2109, 2110, 2111, 2112, 2113, 2114, 2196, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2211, 2212, 2222, 2293],
        'Charlestown ' : [2129],
        'Dorchester' : [2122, 2124, 2125],
        'East Boston' : [2128, 2228],
        'Fenway/Kenmore' : [2115, 2215],
        'Hyde Park' : [2136],
        'Jamaica Plain' : [2130],
        'Mattapan' : [2126],
        'Roslindale' : [2131],
        'Roxbury' : [2119, 2120, 2121],
        'South Boston' : [2127, 2210],
        'South End' : [2118],
        'West Roxbury' : [2132]
    }

data = pd.read_csv('data/food_drink_licenses.csv')

# map data to neighborhood
zip_to_neighborhood = {z: n for n, zips in ZIPS_BY_NEIGHBORHOOD.items() for z in zips}
data['neighborhood'] = data['zip'].map(zip_to_neighborhood)

# drop rows that can't be mapped
data = data.dropna(subset=['neighborhood'])

# classify alcohol vs. no liquor
data['alcohol_label'] = data['license_type'].str.contains('No Liquor', case=False, na=False)
data['alcohol_label'] = data['alcohol_label'].map({False: 'Has Alcohol', True: 'No Liquor'})

# Overall alcohol vs. no liquor bar chart
overall_counts = data['alcohol_label'].value_counts()
overall_counts.plot(kind='bar', figsize=(6,4), color=['steelblue', 'steelblue'],
                    title='Alcohol vs. No Liquor Licenses (Overall)')
plt.xlabel('License Type')
plt.ylabel('Number of Licenses')
plt.legend(title='License Type')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('alcohol_by_neighborhood.png')
plt.show()

# proportion of alcohol licenses per neighborhood
alcohol_by_neighborhood = data.groupby(['neighborhood', 'alcohol_label']).size().unstack(fill_value=0)
alcohol_by_neighborhood['pct_alcohol'] = (
    alcohol_by_neighborhood['Has Alcohol'] / 
    (alcohol_by_neighborhood['Has Alcohol'] + alcohol_by_neighborhood['No Liquor']) * 100
)
alcohol_by_neighborhood['pct_alcohol'].sort_values().plot(
    kind='bar', figsize=(12,5), color='steelblue', 
    title = '% of Businesses with Alcohol License by Neighborhood'
    )
plt.xlabel('Neighborhood')
plt.ylabel('% with Alcohol License')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('alcohol_pct_by_neighborhood.png')
plt.show()

print("\nAlcohol license % by neighborhood: ")
print(alcohol_by_neighborhood['pct_alcohol'].sort_values(ascending=False).round(1))

# Business age by neighborhood: box plot
data = data.dropna(subset=['neighborhood'])
data['issued'] = pd.to_datetime(data['issued'], errors='coerce')
data['age_years'] = (pd.Timestamp.today() - data['issued']).dt.days / 365
age_by_neighborhood = [data[data['neighborhood'] == n]['age_years'].dropna()
                       for n in sorted(data['neighborhood'].unique())]
labels = sorted(data['neighborhood'].unique())

plt.figure(figsize=(14,6))
plt.boxplot(age_by_neighborhood, tick_labels=labels)
plt.xticks(rotation=45, ha='right')
plt.title('Distribution of Business Age by Neighborhood')
plt.xlabel('Neighborhood')
plt.ylabel('Business Age (Years)')
plt.tight_layout()
plt.savefig('boxplot_age_by_neighborhood.png')
plt.show()