'''
Fetches data from the csv stored in Git.
Creates a dataframe of businesses.
Cleans data (removes irrelevant license types, remove repeat businesses)
Adds zip code column in dataframe
Adds calculated age of the business in dataframe
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FILEPATH = 'data/food_drink_licenses.csv'

EXCLUDED_TYPES = [
        'Dormitory',
        'Lodging Houses (Frat/Dorm)',
        'SPCMWA'
    ]

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

def create_businesses(filepath=FILEPATH):
    '''
    Attributes:
        Filepath to repository food/drink license csv
    Returns:
        Dataframe of businesses with specified columns
    '''
    data = pd.read_csv(filepath)
    business_table = data    
    df = pd.DataFrame(business_table)
    df.columns.tolist()
    print("Number of businesses in dataset: ", len(df))
    return df

def revise_business_name(business_data):
    '''
    Revises businesses to "DBA" name or address.
    Attributes: 
        businesses dataframe
    '''
    pass

def remove_repeat_locations(business_data):
    '''
    Removes businesses with the same exact gps coordinates.
    Attributes: 
        businesses dataframe
    '''
    pass

def remove_businesses(business_data, excluded_types=EXCLUDED_TYPES):
    '''
    Removes businesses with irrelevant license types, such as dormitories.
    Gets rid of unwanted business types.
    '''
    before = len(business_data)
    mask = business_data['license_type'].isin(excluded_types)
    filtered_data = business_data[mask == False]
    after = len(filtered_data)

    print(f"Removed {before - after} businesses based on {EXCLUDED_TYPES} license type ({after} remaining)")
    return filtered_data

def encode_neighborhoods(businesses_df):
    '''
    Encode neighborhoods from given zipcodes
    This is important to include because in the raw data a ton are just labelled as "Boston"
    '''
    missing_zips = businesses_df[businesses_df['zip'].isna()]
    print(f"{len(missing_zips)} businesses with missing zip codes.")

    zip_to_neighborhood = {}
    for neighborhood, zips in ZIPS_BY_NEIGHBORHOOD.items():
        for zip_code in zips:
            zip_to_neighborhood[zip_code] = neighborhood
    businesses_df['neighborhood_revised'] = businesses_df['zip'].map(zip_to_neighborhood)

    return businesses_df

def count_businesses_by_zip(business_table):
    '''
    Attributes:
        business dataframe

    Returns:
        Number of businesses in each zip code
    '''
    counts = business_table['zip'].value_counts().sort_index()
    
    #for zipcode, count in counts.items():
    #    print(f"{zipcode}: {count}")

    zip_counts = business_table['zip'].value_counts()
    neighborhood_counts = {}

    for neighborhood, zip_list in ZIPS_BY_NEIGHBORHOOD.items():
        total = 0
        for z in zip_list:
            if z in zip_counts:
                total += zip_counts[z]
        neighborhood_counts[neighborhood] = total

    zip_series = pd.Series({
        z: neighborhood
        for neighborhood, zips in ZIPS_BY_NEIGHBORHOOD.items()
        for z in zips
    })

    business_table['neighborhood_revised'] = business_table['zip'].map(zip_series)
    neighborhood_counts = business_table.groupby('neighborhood_revised').size()

    for neighborhood, count in neighborhood_counts.items():
        return f"{neighborhood}: {count}"

    return neighborhood_counts

def compute_business_age(business_data):
    '''
    Given the dataframe, compute and add a column 'age_years' of the average age of a business
    '''
    business_data = business_data.copy()
    business_data['issued'] = pd.to_datetime(business_data['issued'], errors='coerce')
    today = pd.Timestamp.today()
    business_data['age_years'] = (today - business_data['issued']).dt.days / 365
    return business_data

def find_avg_biz_age_by_key(business_data, key):
    '''
    Given a dataframe of businesses, find the year they were first issued - today, average by key
    '''

    if key == 'neighborhood': 
        avg_age = business_data.groupby('neighborhood_revised')['age_years'].mean().round(2) 
    return avg_age


def plot_mean_biz_age_by_filtering(business_data):
    '''
    Plot the average business data before and after initial filtering by business type.
    Still need to add more filtering, and data from broader sources.
    '''
    avg_age_prefilter = business_data.groupby('neighborhood_revised')['age_years'].mean()
    df_filtered = keep_relevant_businesses(business_data)
    avg_age_postfilter = df_filtered.groupby('neighborhood_revised')['age_years'].mean()

    x = np.arange(len(ZIPS_BY_NEIGHBORHOOD))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, avg_age_prefilter, width, label='Before Filtering')
    rects2 = ax.bar(x + width/2, avg_age_postfilter, width, label='After Filtering')

    ax.set_ylabel('Average Business Age (years)')
    ax.set_title('Average Business Age by Neighborhood')
    ax.set_xticks(x)
    ax.set_xticklabels(ZIPS_BY_NEIGHBORHOOD, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    plt.savefig("avg_business_age_by_neighborhood.png")
    print("Plot saved as avg_business_age_by_neighborhood.png")

def main():
    df = create_businesses()
    df = compute_business_age(df)
    df = remove_businesses(df)
    print(df.head(10))
    df = encode_neighborhoods(df)
    print(df.head(10))
    #count_businesses_by_zip(df)

if __name__ == '__main__':
    main()
    '''
    print(df.head(10))
    print("Number of businesses by neighborhood: \n", df['neighborhood_revised'].value_counts(dropna=False).tolist())
    print("Average business age by neighborhood: \n", find_avg_biz_age_by_key(df, 'neighborhood').tolist())
    plot_mean_biz_age_by_filtering(df)
    '''

