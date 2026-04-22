'''
Predicts whether a Boston business is currently active (is_active=True)
based on location, age, neighborhood, and business category.

Complements hypothesis_tests.py (same data: businesstypes.csv, same
shared.py utilities). DS2500-only methods: KNN classification, K-Means
clustering, StandardScaler, LabelEncoder, train_test_split, plus
accuracy / precision / recall / confusion-matrix metrics.

Required Milestone 4 metrics: Accuracy, Precision, Recall, Confusion matrix.
Required Milestone 4 techniques: K-Means clustering on GPS.

Usage:
    python src/modeling.py        # from repo root
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, confusion_matrix)

from shared import DATA_FILE, ZIP_TO_NEIGHBORHOOD, categorize_business_type

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# Boston sits ~42°N: scale lon by cos(lat) for meter-accurate distance.
BOSTON_LAT = 42.36
LAT_KM = 111.0
LON_KM = LAT_KM * np.cos(np.radians(BOSTON_LAT))
NEAR_RADIUS_KM = 0.3    # 300m  —  same as hypothesis test
K_CLUSTERS = 4          # one per observed neighborhood
K_NEIGHBORS = 5         # KNN's k
RANDOM_STATE = 42


# Data loading + feature engineering

def count_nearby_all(df, radius_km=NEAR_RADIUS_KM):
    '''Count how many other businesses lie within `radius_km` of each row.

    Parameters
        df (pd.DataFrame): Must contain 'latitude' and 'longitude' columns
            in decimal degrees (EPSG:4326).
        radius_km (float): Search radius in kilometers. Defaults to 0.3
            (300 m), matching hypothesis04_test.py.

    Returns
        np.ndarray[int]: One integer per row — the count of OTHER businesses
        within the radius (the row itself is excluded via the `- 1`).

    Assumptions
        - Uses a scaled-Euclidean metric with cos(42°) longitude correction;
          accurate to <0.1% at a 300 m radius around Boston, degrades for
          larger radii or points far from BOSTON_LAT.
        - Rows with NaN lat/lon must be dropped before calling — NaN
          distances will compare False and silently under-count.
    '''
    lat = df['latitude'].values
    lon = df['longitude'].values
    counts = np.zeros(len(df), dtype=int)
    for i in range(len(df)):
        dlat = (lat - lat[i]) * LAT_KM
        dlon = (lon - lon[i]) * LON_KM
        counts[i] = (np.sqrt(dlat ** 2 + dlon ** 2) < radius_km).sum() - 1
    return counts


def load_and_prepare():
    '''Load businesstypes.csv and engineer the four modeling features + target.

    Parameters
        None. Reads shared.DATA_FILE from disk.

    Returns
        pd.DataFrame: Cleaned dataframe with the following added columns —
            - nearby_count (int): businesses within 300 m (location density)
            - age_years (float): years since Date of Filing
            - neighborhood (str): re-derived from shared.ZIP_TO_NEIGHBORHOOD
            - business_category (str): Abby's 9-category filter from shared.py
        The target column `is_active` (bool) is also guaranteed non-null.

    Assumptions
        - DATA_FILE points to a CSV with columns: Zipcode, Date of Filing,
          business_type_clean, latitude, longitude, is_active.
        - Drops any row with NaN in the feature or target columns.
        - Restricts to Boston-metro bounding box (lat 42.20–42.42,
          lon -71.25 to -70.90) to discard ~11 rows with garbage geocoding
          from a MapTiler fallback (e.g. points in Singapore, Wyoming).
    '''
    df = pd.read_csv(DATA_FILE)
    df['Zipcode'] = pd.to_numeric(df['Zipcode'], errors='coerce')
    df['neighborhood'] = df['Zipcode'].map(ZIP_TO_NEIGHBORHOOD)
    df['business_category'] = df['business_type_clean'].apply(
        categorize_business_type)
    # businesstypes.csv doesn't carry age_years directly; derive it from
    # Date of Filing so we don't need the compiled_data1 pipeline.
    df['Date of Filing'] = pd.to_datetime(df['Date of Filing'],
                                           errors='coerce')
    today = pd.Timestamp.today()
    df['age_years'] = (today - df['Date of Filing']).dt.days / 365.25
    df = df.dropna(subset=['latitude', 'longitude', 'is_active',
                           'neighborhood', 'age_years', 'business_category'])
    # 11 rows have garbage geocoding (Singapore, Wyoming, etc. from a
    # MapTiler fallback). Restrict to Boston metro bounding box.
    df = df[(df['latitude'].between(42.20, 42.42))
            & (df['longitude'].between(-71.25, -70.90))]
    df = df.reset_index(drop=True)
    df['nearby_count'] = count_nearby_all(df)
    return df


# KNN classification

def run_classification(df):
    '''Train a KNN classifier to predict business survival and report metrics.

    Parameters
        df (pd.DataFrame): Output of `load_and_prepare()`. Must contain
            columns: nearby_count, age_years, neighborhood, business_category,
            is_active.

    Returns
        None. Prints accuracy / precision / recall / confusion matrix to
        stdout and writes the confusion-matrix heatmap to
        outputs/modeling_confusion_matrix.png.

    Assumptions
        - Mutates `df` in place by adding label-encoded columns `nhd_enc`
          and `cat_enc`.
        - Uses an 80/20 stratified split (random_state=42) so active/closed
          ratio is preserved in both halves.
        - Features are standardized (StandardScaler) so KNN distances aren't
          dominated by age_years (range ~0-30) over nhd_enc (range ~0-3).
        - k = K_NEIGHBORS (5). Precision/recall use is_active=1 as the
          positive class.
    '''
    print('\n' + '=' * 60)
    print('PART 1 — CLASSIFICATION: KNN predicts business survival')
    print('=' * 60)

    # Label-encode categorical features so KNN sees numbers
    df['nhd_enc'] = LabelEncoder().fit_transform(df['neighborhood'])
    df['cat_enc'] = LabelEncoder().fit_transform(df['business_category'])

    feat_cols = ['nearby_count', 'age_years', 'nhd_enc', 'cat_enc']
    X = df[feat_cols].values
    y = df['is_active'].astype(int).values
    print(f'Total samples: {len(df)}   (active={y.sum()}, closed={(1-y).sum()})')
    print(f'Features: {feat_cols}')

    # Stratified 80/20 split preserves active/closed ratio in both halves.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)

    # Scale features so KNN distances aren't dominated by age_years (0-30)
    # swamping nhd_enc (0-3).
    scaler = StandardScaler().fit(X_train)
    X_train_s = scaler.transform(X_train)
    X_test_s = scaler.transform(X_test)

    knn = KNeighborsClassifier(n_neighbors=K_NEIGHBORS)
    knn.fit(X_train_s, y_train)
    y_pred = knn.predict(X_test_s)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print(f'\nKNN (k={K_NEIGHBORS}) — test set (n={len(y_test)}):')
    print(f'  Accuracy  = {acc:.3f}')
    print(f'  Precision = {prec:.3f}   (predicted active that are truly active)')
    print(f'  Recall    = {rec:.3f}   (truly active that we correctly caught)')
    print(f'\nConfusion matrix:')
    print(f'                          predicted closed  predicted active')
    print(f'  actual closed  (0):     {cm[0,0]:>15d}   {cm[0,1]:>15d}')
    print(f'  actual active  (1):     {cm[1,0]:>15d}   {cm[1,1]:>15d}')

    # Heat-mapped confusion matrix figure
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(cm, cmap='Blues')
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(['Closed', 'Active'])
    ax.set_yticklabels(['Closed', 'Active'])
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title(f'KNN Confusion Matrix  (k={K_NEIGHBORS}, accuracy={acc:.2f})')
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                    color='white' if cm[i, j] > cm.max() / 2 else 'black',
                    fontsize=14)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'modeling_confusion_matrix.png', dpi=150)
    plt.close()
    print(f'\nSaved: outputs/modeling_confusion_matrix.png')

# K-Means clustering on GPS

def run_clustering(df):
    '''Run K-Means on GPS coordinates and report per-cluster survival rates.

    Parameters
        df (pd.DataFrame): Output of `load_and_prepare()`. Must contain
            'latitude', 'longitude', and 'is_active' columns.

    Returns
        None. Prints a per-cluster survival table (n, active, survival_pct)
        to stdout and writes a colored cluster map to
        outputs/modeling_kmeans_map.png.

    Assumptions
        - Mutates `df` in place by adding a `cluster` column (0 … K-1).
        - Clusters on raw (lat, lon) WITHOUT cos(lat) correction — this is
          fine for Boston's small latitude range but would bias clusters
          for wider geographies.
        - k = K_CLUSTERS (4), chosen to roughly match observed
          neighborhoods; n_init=10, random_state=42 for reproducibility.
    '''
    print('\n' + '=' * 60)
    print('PART 2 — K-MEANS CLUSTERING on GPS')
    print('=' * 60)

    X = df[['latitude', 'longitude']].values
    km = KMeans(n_clusters=K_CLUSTERS, n_init=10, random_state=RANDOM_STATE)
    df['cluster'] = km.fit_predict(X)

    surv = df.groupby('cluster').agg(
        n=('is_active', 'size'),
        active=('is_active', 'sum'),
        survival_pct=('is_active', lambda x: x.mean() * 100),
    ).round(1)
    print(f'\nSurvival rate by cluster  (k={K_CLUSTERS}):')
    print(surv)

    # Cluster map
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.tab10(np.linspace(0, 1, K_CLUSTERS))
    for c in range(K_CLUSTERS):
        mask = df['cluster'] == c
        ax.scatter(df.loc[mask, 'longitude'], df.loc[mask, 'latitude'],
                   color=colors[c], alpha=0.5, s=20,
                   label=(f'Cluster {c}: n={mask.sum()}, '
                          f"{surv.loc[c, 'survival_pct']:.0f}% active"))
    ax.scatter(km.cluster_centers_[:, 1], km.cluster_centers_[:, 0],
               marker='X', c='black', s=250, linewidths=2,
               edgecolors='white', label='cluster centers')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(f'K-Means Geographic Clusters of Boston Businesses  '
                 f'(k={K_CLUSTERS}, n={len(df)})')
    ax.legend(fontsize=9, loc='best')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'modeling_kmeans_map.png', dpi=150)
    plt.close()
    print(f'Saved: outputs/modeling_kmeans_map.png')


# Main

def main():
    '''Entry point: load data, run KNN classification, run K-Means clustering.

    Parameters
        None.

    Returns
        None. Side effects: prints progress + metrics to stdout and writes
        two figures into outputs/.
    '''
    print('=' * 60)
    print('BUSINESS SUCCESS MODELING')
    print('=' * 60)
    df = load_and_prepare()
    print(f'Loaded {len(df)} businesses from data/businesstypes.csv')
    run_classification(df)
    run_clustering(df)
    print('\n' + '=' * 60)
    print('Done.')
    print('=' * 60)


if __name__ == '__main__':
    main()
