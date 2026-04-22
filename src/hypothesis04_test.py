'''
H4: Food & Drink Cluster Density vs Survival
"There are neighborhoods with greater clusters of restaurants in close
vicinity. These are more successful than businesses far from other
businesses/restaurants."

Data: data/businesstypes.csv (DBA-derived dataset with is_active signal).
    Not compiled_data1.csv: every non-null row there has status=='Active'
    (no closure variation; can't measure survival).
    Not food_drink_licenses.csv: also all Active (Boston Open Data returns
    only currently-licensed establishments).
    businesstypes.csv is the only file with a real active/closed split.

Filter: uses `categorize_business_type` from shared.py to keep the
"Food & Drink" definition consistent across the codebase. includes
restaurants, cafes, coffee shops, pubs, pizza, bakeries, and generic
'food' categories.

Neighborhood mapping: uses ZIPS_BY_NEIGHBORHOOD from shared.py as the
single source of truth for zip->neighborhood assignment.

Usage:
    python src/hypothesis_tests.py
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

from shared import DATA_FILE, ZIP_TO_NEIGHBORHOOD, categorize_business_type

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# Boston sits near 42°N. One degree of latitude ≈ 111 km; one degree of
# longitude ≈ cos(42°) * 111 ≈ 82 km. Scaling longitude by cos(lat) gives
# us a locally-flat metric accurate to <0.1% at a 300m radius.
BOSTON_LAT = 42.36
LAT_KM = 111.0
LON_KM = LAT_KM * np.cos(np.radians(BOSTON_LAT))
CLUSTER_RADIUS_KM = 0.3  # 300 m


def load_food_and_drink():
    '''Load businesstypes.csv and return only Food & Drink businesses.

    Parameters
        None. Reads shared.DATA_FILE from disk.

    Returns
        pd.DataFrame: Food & Drink subset with columns including 'latitude',
        'longitude', 'is_active', 'neighborhood', and 'business_category',
        reset-indexed.

    Assumptions
        - DATA_FILE must contain 'Zipcode', 'business_type_clean',
          'latitude', 'longitude', and 'is_active' columns.
        - Neighborhood is re-derived from shared.ZIP_TO_NEIGHBORHOOD (single
          source of truth) rather than trusting whatever was baked into
          businesstypes.csv at preprocessing time.
        - Category filter uses shared.categorize_business_type so
          "Food & Drink" matches the rest of the codebase (restaurants,
          cafes, coffee shops, pubs, pizza, bakeries, generic 'food').
        - Drops rows with NaN lat/lon/is_active and restricts to the Boston
          bounding box (42.20-42.42 lat, -71.25 to -70.90 lon) to discard
          a geocoding-failure row mapped to Italy.
    '''
    df = pd.read_csv(DATA_FILE)

    # re-derive neighborhood from the global zip map
    df['Zipcode'] = pd.to_numeric(df['Zipcode'], errors='coerce')
    df['neighborhood'] = df['Zipcode'].map(ZIP_TO_NEIGHBORHOOD)

    # apply shared categorization filter
    df['business_category'] = df['business_type_clean'].apply(
        categorize_business_type)
    fd = df[df['business_category'] == 'Food & Drink'].copy()
    fd = fd.dropna(subset=['latitude', 'longitude', 'is_active'])
    # drop geocoding-failure rows (one F&D business got mapped to Italy)
    # so the scatter plot is scaled to Boston, not the globe.
    fd = fd[(fd['latitude'].between(42.20, 42.42))
            & (fd['longitude'].between(-71.25, -70.90))]
    return fd.reset_index(drop=True)


def count_nearby(df, radius_km=CLUSTER_RADIUS_KM):
    '''Count how many other F&D businesses lie within `radius_km` of each row.

    Parameters
        df (pd.DataFrame): Must contain 'latitude' and 'longitude' columns
            in decimal degrees (EPSG:4326).
        radius_km (float): Search radius in kilometers. Defaults to 0.3
            (300 m), the cluster threshold used for H4 binning.

    Returns
        np.ndarray[int]: One integer per row — the count of OTHER F&D
        businesses within the radius (the row itself is excluded).

    Assumptions
        - Uses a scaled-Euclidean metric with cos(42°) longitude correction;
          accurate to <0.1% at 300 m around Boston, degrades farther out.
        - `df` should already be filtered to Food & Drink — the "other F&D"
          count is only meaningful against the same categorical population.
        - Rows with NaN lat/lon must be dropped beforehand, otherwise NaN
          distances compare False and the count silently under-reports.
    '''
    lat = df['latitude'].values
    lon = df['longitude'].values
    counts = np.zeros(len(df), dtype=int)
    for i in range(len(df)):
        dlat = (lat - lat[i]) * LAT_KM
        dlon = (lon - lon[i]) * LON_KM
        counts[i] = (np.sqrt(dlat ** 2 + dlon ** 2) < radius_km).sum() - 1
    return counts


def test_h4(df):
    '''Run the H4 cluster-density survival test on a Food & Drink dataframe.

    For every business, counts neighbors within CLUSTER_RADIUS_KM, bins the
    result into Isolated / Low / High density tiers, and prints a survival
    table. Tests the hypothesis with a point-biserial correlation between
    is_active (binary) and nearby-count (continuous).

    Parameters
        df (pd.DataFrame): Food & Drink subset (output of
            `load_food_and_drink()`). Must contain 'latitude', 'longitude',
            and boolean 'is_active' columns.

    Returns
        None. Side effects:
            - Prints a survival-by-cluster table, r, p, and verdict string.
            - Writes outputs/h4_cluster_survival.png (bar chart) and
              outputs/h4_cluster_map.png (geographic scatter, blue=active,
              coral=closed, size ∝ nearby density).

    Assumptions
        - Mutates `df` in place by adding 'nearby' (int) and 'cluster_bin'
          (categorical: 'Isolated (0)' / 'Low (1-4)' / 'High (5+)') columns.
        - Uses 3 bins, not 5 — with only ~39 closures in the dataset,
          finer bins give cells of 2-3 closed restaurants and unstable
          survival-rate estimates.
        - Verdict thresholds: r > 0 AND p < 0.05 => "SUPPORTS";
          r > 0 AND p >= 0.05 => "Directionally supports but not significant";
          r <= 0 => "Does NOT support".
    '''
    n_active = int(df['is_active'].sum())
    n_closed = int((~df['is_active']).sum())
    print(f'Food & Drink businesses: {len(df)}  '
          f'({n_active} active, {n_closed} closed)')

    df['nearby'] = count_nearby(df)

    # 3 bins (not 5) — only 39 closures total, so finer bins give cells of
    # 2-3 closed restaurants and unstable survival-rate estimates.
    df['cluster_bin'] = pd.cut(
        df['nearby'],
        bins=[-1, 0, 4, 1000],
        labels=['Isolated (0)', 'Low (1-4)', 'High (5+)']
    )

    survival = df.groupby('cluster_bin', observed=False).agg(
        n=('is_active', 'size'),
        closed=('is_active', lambda x: int((~x).sum())),
        survival_pct=('is_active', lambda x: x.mean() * 100),
    ).round(1)
    print('\n--- Survival by cluster density ---')
    print(survival)

    # Point-biserial: binary (is_active) vs continuous (nearby count).
    # Positive r => more neighbors correlated with survival (supports H4).
    r, p = stats.pointbiserialr(df['is_active'].astype(int), df['nearby'])
    print(f'\nPoint-biserial correlation:  r = {r:.4f},  p = {p:.4f}')
    if r > 0 and p < 0.05:
        verdict = 'SUPPORTS the hypothesis (significant positive correlation).'
    elif r > 0:
        verdict = 'Directionally supports but NOT statistically significant.'
    else:
        verdict = 'Does NOT support the hypothesis.'
    print(f'Verdict: {verdict}')

    # --- bar chart ---
    fig, ax = plt.subplots(figsize=(8, 5))
    survival['survival_pct'].plot(kind='bar', color='steelblue', ax=ax)
    ax.set_xlabel('Other Food & Drink businesses within 300 m')
    ax.set_ylabel('Survival rate (%)')
    ax.set_title(f'H4: Food & Drink cluster density vs survival  (n = {len(df)})')
    ax.set_ylim(0, 105)
    for i, (_, row) in enumerate(survival.iterrows()):
        ax.text(i, row['survival_pct'] + 1,
                f"{row['survival_pct']:.0f}%\nn={row['n']}",
                ha='center', fontsize=9)
    ax.set_xticklabels(survival.index, rotation=0)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'h4_cluster_survival.png', dpi=150)
    plt.close()
    print(f"\nSaved: outputs/h4_cluster_survival.png")

    # --- map ---
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = df['is_active'].map({True: 'steelblue', False: 'coral'})
    sizes = df['nearby'] * 5 + 15
    ax.scatter(df['longitude'], df['latitude'], c=colors, s=sizes,
               alpha=0.6, edgecolors='white', linewidth=0.3)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Food & Drink businesses — blue = active, coral = closed, '
                 'size ∝ nearby F&D density')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'h4_cluster_map.png', dpi=150)
    plt.close()
    print(f"Saved: outputs/h4_cluster_map.png")


def main():
    '''Entry point: load Food & Drink subset and run the H4 cluster test.

    Parameters
        None.

    Returns
        None. Side effects: prints the H4 survival table + correlation
        results to stdout and writes two figures to outputs/.
    '''
    print('=' * 60)
    print('H4: Food & Drink businesses in dense clusters are more successful')
    print('=' * 60)
    df = load_food_and_drink()
    test_h4(df)


if __name__ == '__main__':
    main()
