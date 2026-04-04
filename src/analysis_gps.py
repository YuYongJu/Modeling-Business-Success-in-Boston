import pandas as pd
import numpy as np

import fetch_foodanddrink as licences
import fetch_mbtaAPI as mbta

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


def analyze_gps():
    API = create_API_variables()
    call_API_load(API)

def main():
    foodanddrink_data = fetch_foodanddrink.main()

if __name__ == '__main__':
    main()