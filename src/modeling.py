'''
Business Success Modeling for Boston Storefronts
DS2500 - Section 01

Three modeling approaches:
  1. Classification (KNN + Logistic Regression): predicts whether a
     business has closed. Features: neighborhood, business category,
     diversity score, MBTA distance
  2. Linear Regression: predicts business duration (years open)
  3. K-Means Clustering: groups businesses by GPS location, analyzes
     survival rate and business diversity by geographic cluster

Models: KNN (k=5), Logistic Regression, Linear Regression, K-Means
Metrics: Accuracy, Precision, Recall, Confusion Matrix, R², MAE
'''

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix,
                             mean_absolute_error, r2_score)

# zip codes in the DBA dataset mapped to neighborhoods
ZIPS_BY_NEIGHBORHOOD = {
    'Back Bay/Beacon Hill': [2108, 2116],
    'Fenway/Kenmore': [2115],
    'Roxbury': [2120],
    'South Boston': [2127],
}

# keyword-based groupings to collapse ~1900 raw business types into categories
BUSINESS_CATEGORIES = {
    'restaurant': ['restaurant', 'cafe', 'bakery', 'pizza', 'diner', 'sushi',
                   'food truck', 'catering', 'deli', 'bar & grill', 'tavern',
                   'pub', 'bar', 'grill', 'bistro', 'eatery', 'kitchen',
                   'bbq', 'ramen', 'noodle', 'thai', 'chinese', 'mexican',
                   'italian', 'indian', 'japanese', 'korean', 'vietnamese',
                   'mediterranean', 'burger', 'wings', 'seafood', 'steakhouse',
                   'brunch', 'breakfast', 'lunch', 'dinner', 'takeout',
                   'food service', 'food'],
    'retail': ['retail', 'store', 'shop', 'boutique', 'market', 'grocery',
               'convenience store', 'liquor store', 'wine', 'tobacco',
               'clothing', 'apparel', 'fashion', 'jewelry', 'florist',
               'flower', 'gift', 'thrift', 'vintage', 'antique', 'bookstore',
               'pet store', 'hardware', 'electronics', 'furniture',
               'home goods', 'sporting goods', 'art gallery', 'gallery',
               'online retail'],
    'beauty_wellness': ['hair salon', 'salon', 'barber', 'spa', 'nail',
                        'beauty', 'cosmetic', 'skincare', 'waxing', 'tattoo',
                        'massage', 'wellness', 'yoga', 'fitness', 'gym',
                        'pilates', 'personal training'],
    'professional_services': ['consulting', 'law firm', 'attorney', 'legal',
                              'accounting', 'financial', 'insurance',
                              'marketing', 'advertising', 'design',
                              'architecture', 'engineering', 'it services',
                              'software', 'technology', 'web design',
                              'graphic design', 'photography', 'media',
                              'public relations', 'staffing', 'recruitment',
                              'translation', 'tutoring', 'education'],
    'real_estate': ['real estate', 'property management',
                    'real estate brokerage', 'mortgage lending', 'mortgage',
                    'realty', 'rental', 'short term rental', 'airbnb'],
    'medical': ['medical', 'dental', 'doctor', 'physician', 'clinic',
                'pharmacy', 'optometry', 'chiropractic', 'therapy',
                'counseling', 'mental health', 'veterinary', 'health'],
    'food_bev_production': ['brewery', 'distillery', 'winery', 'coffee',
                            'tea', 'ice cream', 'candy', 'chocolate',
                            'juice', 'smoothie', 'boba'],
    'automotive': ['auto', 'car', 'vehicle', 'towing', 'mechanic', 'garage',
                   'parking', 'gas station', 'car wash', 'detailing'],
    'construction_trades': ['construction', 'plumbing', 'electrical',
                            'hvac', 'roofing', 'painting', 'landscaping',
                            'cleaning', 'janitorial', 'handyman',
                            'contractor', 'renovation', 'remodeling',
                            'carpentry', 'masonry'],
    'hospitality': ['hotel', 'motel', 'inn', 'lodging', 'hostel',
                    'bed and breakfast', 'event', 'entertainment',
                    'nightclub', 'lounge', 'banquet'],
    'transportation': ['transportation', 'delivery', 'courier', 'moving',
                       'trucking', 'logistics', 'shipping', 'taxi', 'limo',
                       'rideshare'],
}


def categorize_business(biz_type):
    '''Map a raw business type string to a broader category'''
    for category, keywords in BUSINESS_CATEGORIES.items():
        for keyword in keywords:
            if keyword in biz_type:
                return category
    return 'other'


def haversine_km(lat1, lon1, lat2, lon2):
    '''Distance in km between two GPS points using the haversine formula'''
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2
         + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2))
         * np.sin(dlon / 2) ** 2)
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def fetch_mbta_stops():
    '''Fetch MBTA subway/light rail stop coordinates from the public API'''
    try:
        url = 'https://api-v3.mbta.com/stops?filter[route_type]=0,1'
        response = requests.get(url, timeout=10)
        data = response.json()
        stops = [(s['attributes']['latitude'], s['attributes']['longitude'])
                 for s in data['data']]
        print(f'  Fetched {len(stops)} MBTA stops')
        return stops
    except Exception as e:
        print(f'  Warning: could not fetch MBTA stops ({e})')
        return None


def min_distance_to_stops(lat, lon, stops):
    '''Distance in km from a point to the nearest MBTA stop'''
    return min(haversine_km(lat, lon, s[0], s[1]) for s in stops)


def compute_diversity_score(df, radius_deg=0.004):
    '''
    Count unique business categories within ~0.25 miles of each business.
    0 = no neighbors or all same type. Higher = more variety nearby.

    Uses ~0.004 degrees as approximate 0.25-mile radius at Boston's latitude.
    '''
    lats = df['lat'].values
    lons = df['lon'].values
    categories = df['business_category'].values
    scores = np.zeros(len(df), dtype=int)

    for i in range(len(df)):
        dists = np.sqrt((lats - lats[i]) ** 2 + (lons - lons[i]) ** 2)
        nearby_mask = (dists < radius_deg) & (np.arange(len(df)) != i)

        if nearby_mask.sum() == 0:
            scores[i] = 0
        else:
            nearby_cats = set(categories[nearby_mask])
            scores[i] = len(nearby_cats)

    return scores


def load_and_prepare_data(filepath):
    '''Load the DBA CSV and engineer features for modeling'''
    df = pd.read_csv(filepath)

    # parse dates
    df['Date of Filing'] = pd.to_datetime(
        df['Date of Filing'], errors='coerce')
    df['Date of Expiration'] = pd.to_datetime(
        df['Date of Expiration'], errors='coerce')

    # target: is the business closed? (DBA expiration as proxy)
    today = pd.Timestamp.today()
    df['is_closed'] = (df['Date of Expiration'] < today).astype(int)

    # duration: how long the business has been or was open
    #   closed businesses: date of filing -> date of expiration
    #   active businesses: date of filing -> today
    df['duration_years'] = np.where(
        df['is_closed'] == 1,
        (df['Date of Expiration'] - df['Date of Filing']).dt.days / 365.25,
        (today - df['Date of Filing']).dt.days / 365.25
    )

    # neighborhood from zip code
    zip_to_neighborhood = {}
    for neighborhood, zips in ZIPS_BY_NEIGHBORHOOD.items():
        for z in zips:
            zip_to_neighborhood[z] = neighborhood
    df['neighborhood'] = df['Zipcode'].map(zip_to_neighborhood)

    # business category from raw type text
    df['biz_type_clean'] = (df['Type of Business']
                            .fillna('unknown').str.strip().str.lower())
    df['business_category'] = df['biz_type_clean'].apply(categorize_business)

    # GPS-derived features
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['lat'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['lon'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])

        # diversity score: unique business types within ~0.25 miles
        print('  Computing diversity scores...')
        df = df.reset_index(drop=True)
        df['diversity_score'] = compute_diversity_score(df)

        # distance to nearest MBTA stop
        mbta_stops = fetch_mbta_stops()
        if mbta_stops is not None:
            df['dist_to_mbta'] = df.apply(
                lambda row: min_distance_to_stops(
                    row['lat'], row['lon'], mbta_stops),
                axis=1
            )

    # drop rows missing critical values or bad data
    df = df.dropna(subset=['neighborhood', 'duration_years', 'is_closed'])
    df = df[df['duration_years'] >= 0]  # remove entries where expiration < filing

    return df


# =========================================================================
# PART 1: KNN Classification
# =========================================================================

def run_classification(df):
    '''Predict whether a business is closed using KNN and Logistic Regression'''
    print('\n' + '=' * 60)
    print('PART 1: CLASSIFICATION (KNN + Logistic Regression)')
    print('=' * 60)

    le_n = LabelEncoder()
    le_c = LabelEncoder()
    df = df.copy()
    df['neighborhood_enc'] = le_n.fit_transform(df['neighborhood'])
    df['category_enc'] = le_c.fit_transform(df['business_category'])

    # features an entrepreneur would know before opening
    feature_cols = ['neighborhood_enc', 'category_enc']
    feature_names = ['Neighborhood', 'Business Category']

    if 'diversity_score' in df.columns:
        feature_cols.append('diversity_score')
        feature_names.append('Diversity Score')
    if 'dist_to_mbta' in df.columns:
        feature_cols.append('dist_to_mbta')
        feature_names.append('Dist to MBTA (km)')

    X = df[feature_cols].values
    y = df['is_closed'].values

    print(f'Features: {feature_names}')
    print(f'Dataset: {len(df)} businesses')
    print(f'  Active: {(y == 0).sum()} ({(y == 0).mean():.1%})')
    print(f'  Closed: {(y == 1).sum()} ({(y == 1).mean():.1%})')

    # 80/20 train/test split, stratified to preserve class balance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f'Train: {len(X_train)}, Test: {len(X_test)}')

    # scale features so KNN distances are not dominated by one feature
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # train both models
    models = {
        'KNN (k=5)': KNeighborsClassifier(n_neighbors=5),
        'Logistic Regression': LogisticRegression(max_iter=1000,
                                                  random_state=42),
    }

    all_results = {}
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        all_results[name] = {
            'accuracy': acc, 'precision': prec, 'recall': rec,
            'f1': f1, 'confusion_matrix': cm, 'model': model,
        }

        print(f'\n{name}:')
        print(f'  Accuracy:  {acc:.4f}')
        print(f'  Precision: {prec:.4f}')
        print(f'  Recall:    {rec:.4f}')
        print(f'  F1 Score:  {f1:.4f}')

    # plot confusion matrices side by side
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for idx, (name, res) in enumerate(all_results.items()):
        cm = res['confusion_matrix']
        im = axes[idx].imshow(cm, cmap='Blues')
        axes[idx].set_xticks([0, 1])
        axes[idx].set_yticks([0, 1])
        axes[idx].set_xticklabels(['Active', 'Closed'])
        axes[idx].set_yticklabels(['Active', 'Closed'])
        axes[idx].set_xlabel('Predicted')
        axes[idx].set_ylabel('Actual')
        axes[idx].set_title(f'{name} (Acc: {res["accuracy"]:.1%})')
        for i in range(2):
            for j in range(2):
                color = 'white' if cm[i][j] > cm.max() / 2 else 'black'
                axes[idx].text(j, i, str(cm[i][j]), ha='center',
                               va='center', fontsize=16, color=color)
    plt.suptitle('Classification — Confusion Matrices', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrices.png'), dpi=150)
    print('\nSaved: outputs/confusion_matrices.png')
    plt.close()

    # EDA visualizations
    plot_closed_by_neighborhood(df)
    plot_closed_by_category(df)

    all_results['scaler'] = scaler
    return all_results


def plot_closed_by_neighborhood(df):
    '''Stacked bar chart: active vs closed by neighborhood'''
    ct = pd.crosstab(df['neighborhood'], df['is_closed'])
    ct.columns = ['Active', 'Closed']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ct.plot(kind='bar', stacked=True, color=['steelblue', 'coral'],
            ax=axes[0])
    axes[0].set_title('Business Count by Neighborhood')
    axes[0].set_ylabel('Number of Businesses')
    axes[0].set_xlabel('')
    axes[0].tick_params(axis='x', rotation=45)

    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    ct_pct.plot(kind='bar', stacked=True, color=['steelblue', 'coral'],
                ax=axes[1])
    axes[1].set_title('Closure Rate by Neighborhood')
    axes[1].set_ylabel('Percentage')
    axes[1].set_xlabel('')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].legend(loc='lower right')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'closed_by_neighborhood.png'),
                dpi=150)
    print('Saved: outputs/closed_by_neighborhood.png')
    plt.close()


def plot_closed_by_category(df):
    '''Horizontal bar chart: closure rate by business category'''
    ct = pd.crosstab(df['business_category'], df['is_closed'])
    ct.columns = ['Active', 'Closed']
    ct['total'] = ct.sum(axis=1)
    ct['closure_rate'] = ct['Closed'] / ct['total'] * 100

    ct = ct[ct['total'] >= 20].sort_values('closure_rate')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(ct.index, ct['closure_rate'], color='coral')
    ax.set_xlabel('Closure Rate (%)')
    ax.set_title('Business Closure Rate by Category (min 20 businesses)')
    ax.axvline(x=ct['closure_rate'].mean(), color='gray', linestyle='--',
               label=f'Mean: {ct["closure_rate"].mean():.1f}%')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'closed_by_category.png'), dpi=150)
    print('Saved: outputs/closed_by_category.png')
    plt.close()


# =========================================================================
# PART 2: Linear Regression — predict business duration
# =========================================================================

def run_duration_regression(df):
    '''Predict how long a business lasts using Linear Regression'''
    print('\n' + '=' * 60)
    print('PART 2: LINEAR REGRESSION (Duration Prediction)')
    print('=' * 60)

    le_n = LabelEncoder()
    le_c = LabelEncoder()
    df = df.copy()
    df['neighborhood_enc'] = le_n.fit_transform(df['neighborhood'])
    df['category_enc'] = le_c.fit_transform(df['business_category'])

    X = df[['neighborhood_enc', 'category_enc']].values
    y = df['duration_years'].values

    print(f'Target: business duration (years)')
    print(f'Features: Neighborhood, Business Category')
    print(f'Duration range: {y.min():.1f} to {y.max():.1f} years')
    print(f'Mean duration: {y.mean():.1f} years')

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print(f'\nResults (Linear Regression):')
    print(f'  R² Score: {r2:.4f}')
    print(f'  MAE:      {mae:.2f} years')

    # predicted vs actual scatter
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_test, y_pred, alpha=0.3, s=10, color='steelblue')
    lims = [0, max(y_test.max(), y_pred.max())]
    ax.plot(lims, lims, 'r--', label='Perfect prediction')
    ax.set_xlabel('Actual Duration (years)')
    ax.set_ylabel('Predicted Duration (years)')
    ax.set_title(f'Linear Regression — Predicted vs Actual (R²={r2:.3f})')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'regression_predicted_vs_actual.png'),
                dpi=150)
    print('Saved: outputs/regression_predicted_vs_actual.png')
    plt.close()

    # average duration by neighborhood
    avg = df.groupby('neighborhood')['duration_years'].mean()
    avg = avg.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    avg.plot(kind='bar', color='steelblue', ax=ax)
    ax.set_ylabel('Average Duration (years)')
    ax.set_title('Average Business Duration by Neighborhood')
    ax.set_xlabel('')
    for i, (neigh, val) in enumerate(avg.items()):
        ax.text(i, val + 0.1, f'{val:.1f}', ha='center', va='bottom',
                fontsize=10)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'avg_duration_by_neighborhood.png'),
                dpi=150)
    print('Saved: outputs/avg_duration_by_neighborhood.png')
    plt.close()

    return {'r2': r2, 'mae': mae, 'model': model}


# =========================================================================
# PART 3: K-Means Clustering — geographic business clusters
# =========================================================================

def run_kmeans_clustering(df):
    '''Cluster businesses by GPS and analyze survival by cluster'''
    if 'lat' not in df.columns or 'lon' not in df.columns:
        print('\nSkipping K-Means: no GPS data')
        return None

    print('\n' + '=' * 60)
    print('PART 3: K-MEANS CLUSTERING (GPS-based)')
    print('=' * 60)

    coords = df[['lat', 'lon']].values

    # try different k values and pick the best separation
    k_range = range(3, 9)
    best_k = 5
    best_score = -1
    print('Testing cluster counts (silhouette = how well-separated):')
    from sklearn.metrics import silhouette_score
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(coords)
        score = silhouette_score(coords, labels)
        print(f'  k={k}: silhouette={score:.4f}')
        if score > best_score:
            best_score = score
            best_k = k

    print(f'Best k={best_k} (silhouette={best_score:.4f})')

    # fit with best k
    km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df = df.copy()
    df['cluster'] = km.fit_predict(coords)

    # plot clusters on map
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    scatter = axes[0].scatter(df['lon'], df['lat'], c=df['cluster'],
                              cmap='tab10', alpha=0.5, s=8)
    axes[0].set_title(f'Business Clusters (k={best_k})')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    plt.colorbar(scatter, ax=axes[0], label='Cluster')

    colors = df['is_closed'].map({0: 'steelblue', 1: 'coral'})
    axes[1].scatter(df['lon'], df['lat'], c=colors, alpha=0.5, s=8)
    axes[1].set_title('Active (Blue) vs Closed (Red)')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'kmeans_map.png'), dpi=150)
    print('Saved: outputs/kmeans_map.png')
    plt.close()

    # survival rate by cluster
    cluster_stats = df.groupby('cluster').agg(
        count=('is_closed', 'size'),
        survival_rate=('is_closed', lambda x: (1 - x.mean()) * 100),
        avg_duration=('duration_years', 'mean'),
    ).round(1)

    if 'diversity_score' in df.columns:
        div_by_cluster = df.groupby('cluster')['diversity_score'].mean()
        cluster_stats['avg_diversity'] = div_by_cluster.round(1).values

    print('\nCluster Statistics:')
    print(cluster_stats)

    # bar chart of survival by cluster
    fig, ax = plt.subplots(figsize=(10, 5))
    cluster_stats['survival_rate'].plot(kind='bar', color='steelblue', ax=ax)
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Survival Rate (%)')
    ax.set_title('Business Survival Rate by Geographic Cluster')
    overall = (1 - df['is_closed'].mean()) * 100
    ax.axhline(y=overall, color='coral', linestyle='--',
               label=f'Overall: {overall:.1f}%')
    ax.legend()
    for i, v in enumerate(cluster_stats['survival_rate']):
        ax.text(i, v + 0.5, f'{v:.0f}%', ha='center', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'survival_by_cluster.png'), dpi=150)
    print('Saved: outputs/survival_by_cluster.png')
    plt.close()

    # diversity vs survival analysis
    if 'diversity_score' in df.columns:
        df['diversity_level'] = pd.cut(
            df['diversity_score'],
            bins=[-1, 8, 10, 12],
            labels=['Low (0-8)', 'Medium (9-10)', 'High (11-12)']
        )
        div_survival = df.groupby('diversity_level', observed=False).agg(
            count=('is_closed', 'size'),
            survival_rate=('is_closed', lambda x: (1 - x.mean()) * 100)
        ).round(1)
        print('\nDiversity vs Survival:')
        print(div_survival)

        fig, ax = plt.subplots(figsize=(8, 5))
        div_survival['survival_rate'].plot(kind='bar', color='steelblue',
                                           ax=ax)
        ax.set_xlabel('Business Type Diversity Nearby')
        ax.set_ylabel('Survival Rate (%)')
        ax.set_title('Nearby Business Diversity vs Survival Rate')
        for i, v in enumerate(div_survival['survival_rate']):
            ax.text(i, v + 0.5, f'{v:.0f}%', ha='center', fontsize=10)
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'diversity_vs_survival.png'),
                    dpi=150)
        print('Saved: outputs/diversity_vs_survival.png')
        plt.close()

    return df, best_k


# =========================================================================
# Main
# =========================================================================

def main():
    filepath = '../CityofBoston-CityClerkDBA_cleaned.csv'

    print('Loading and preparing data...')
    df = load_and_prepare_data(filepath)

    print(f'\nDataset: {len(df)} businesses')
    print(f'  Active: {(df["is_closed"] == 0).sum()} '
          f'({(df["is_closed"] == 0).mean():.1%})')
    print(f'  Closed: {(df["is_closed"] == 1).sum()} '
          f'({(df["is_closed"] == 1).mean():.1%})')
    print(f'\nNeighborhoods:')
    print(df['neighborhood'].value_counts())
    print(f'\nBusiness categories: {df["business_category"].nunique()}')
    print(df['business_category'].value_counts())

    # Part 1: Classification (KNN + Logistic Regression)
    clf_results = run_classification(df)

    # Part 2: Duration Regression
    reg_results = run_duration_regression(df)

    # Part 3: K-Means Clustering
    cluster_result = run_kmeans_clustering(df)

    # Summary
    print('\n' + '=' * 60)
    print('SUMMARY')
    print('=' * 60)

    print(f'\nPart 1 — Classification (is this business closed?):')
    for name in ['KNN (k=5)', 'Logistic Regression']:
        if name in clf_results:
            r = clf_results[name]
            print(f'  {name}:')
            print(f'    Accuracy={r["accuracy"]:.4f}  '
                  f'Precision={r["precision"]:.4f}  '
                  f'Recall={r["recall"]:.4f}  '
                  f'F1={r["f1"]:.4f}')

    print(f'\nPart 2 — Linear Regression (how long will it last?):')
    print(f'  R²:  {reg_results["r2"]:.4f}')
    print(f'  MAE: {reg_results["mae"]:.2f} years')

    if cluster_result is not None:
        _, best_k = cluster_result
        print(f'\nPart 3 — K-Means Clustering (geographic patterns):')
        print(f'  Clusters: {best_k}')

    print(f'\nAll plots saved to outputs/')


if __name__ == '__main__':
    main()
