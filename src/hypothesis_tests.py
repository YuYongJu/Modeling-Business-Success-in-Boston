'''
Hypothesis 4 Test — Addison Apisarnthanarax
"There are neighborhoods with greater clusters of restaurants in close
vicinity. These are more successful than businesses far from other
businesses/restaurants."

Usage:
    python hypothesis_tests.py
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats
from modeling import load_and_prepare_data, OUTPUT_DIR


def load_data():
    return load_and_prepare_data('../CityofBoston-CityClerkDBA_cleaned.csv')


def test_h4_restaurant_clusters(df):
    '''Restaurants in dense clusters are more successful'''
    print('='*60)
    print('H4: Restaurants in dense clusters are more successful')
    print('='*60)

    if 'lat' not in df.columns:
        print('Skipping: no GPS data')
        return

    restaurants = df[df['business_category'] == 'restaurant'].copy()
    print(f'Restaurants: {len(restaurants)}')

    if len(restaurants) < 20:
        print('Not enough restaurants for analysis')
        return

    radius = 0.003  # ~300m for restaurant clusters
    r_lats = restaurants['lat'].values
    r_lons = restaurants['lon'].values

    nearby_restaurants = np.zeros(len(restaurants), dtype=int)
    for i in range(len(restaurants)):
        dists = np.sqrt((r_lats - r_lats[i])**2 + (r_lons - r_lons[i])**2)
        nearby_restaurants[i] = (dists < radius).sum() - 1

    restaurants['nearby_restaurants'] = nearby_restaurants
    restaurants['cluster_bin'] = pd.cut(restaurants['nearby_restaurants'],
                                        bins=[-1, 0, 3, 8, 15, 100],
                                        labels=['Isolated', '1-3', '4-8', '9-15', '15+'])

    surv = restaurants.groupby('cluster_bin', observed=False).agg(
        count=('is_expired', 'size'),
        survival_rate=('is_expired', lambda x: (1 - x.mean()) * 100)
    ).round(1)
    print(surv)

    # bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    surv['survival_rate'].plot(kind='bar', color='steelblue', ax=ax)
    ax.set_xlabel('Other Restaurants Within ~300m')
    ax.set_ylabel('Survival Rate (%)')
    ax.set_title('H4: Restaurant Cluster Density vs Survival')
    for i, v in enumerate(surv['survival_rate']):
        ax.text(i, v + 0.5, f'{v:.0f}%', ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'h4_restaurant_clusters.png'), dpi=150)
    print('Saved: outputs/h4_restaurant_clusters.png')
    plt.close()

    # map of restaurant clusters colored by survival
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = restaurants['is_expired'].map({0: 'steelblue', 1: 'coral'})
    sizes = restaurants['nearby_restaurants'] * 2 + 5
    ax.scatter(restaurants['lon'], restaurants['lat'], c=colors, s=sizes, alpha=0.6)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Restaurant Locations (Blue=Active, Red=Expired, Size=Cluster Density)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'h4_restaurant_map.png'), dpi=150)
    print('Saved: outputs/h4_restaurant_map.png')
    plt.close()

    # statistical test
    corr, p = stats.pointbiserialr(
        restaurants['is_expired'], restaurants['nearby_restaurants']
    )
    print(f'\nCorrelation (expired vs nearby restaurants): r={corr:.4f}, p={p:.4f}')
    if corr < 0:
        print('Negative = more nearby restaurants → less likely expired (SUPPORTS hypothesis)')
    else:
        print('Positive = more nearby restaurants → more likely expired (contradicts hypothesis)')


def main():
    print('Loading data...')
    df = load_data()
    print(f'Loaded {len(df)} businesses\n')
    test_h4_restaurant_clusters(df)


if __name__ == '__main__':
    main()
