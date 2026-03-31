'''
Business Success Modeling for Boston Storefronts
DS2500 - Addison Apisarnthanarax

Four modeling approaches:
  1. Classification: predicts whether a business has expired (proxy for closure)
     - Full model: neighborhood, business category, age, renewal status
     - Entrepreneur model: only neighborhood + business category (no data leakage)
  2. Regression: predicts business longevity (age in years) from neighborhood
     and business type — directly answers "where should I open my business?"
  3. K-Means Clustering: groups businesses by GPS location, tests whether
     businesses in denser clusters have higher survival rates
  4. Spatial Model: adds GPS-derived features (MBTA distance, cluster density,
     nearby business count) to improve entrepreneur model predictions

Models: Logistic Regression, Decision Tree, Random Forest, KNN, K-Means
Metrics: Accuracy, Precision, Recall, F1, Confusion Matrix, R², MAE
'''

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report,
                             ConfusionMatrixDisplay, mean_absolute_error,
                             r2_score, mean_squared_error, silhouette_score)

# neighborhood mapping from zip codes in DBA dataset
ZIPS_BY_NEIGHBORHOOD = {
    'Back Bay/Beacon Hill': [2108, 2116],
    'Fenway/Kenmore': [2115],
    'Roxbury': [2120],
    'South Boston': [2127],
}

# business type groupings — collapses 1994 raw types into ~12 categories
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
    'real_estate': ['real estate', 'property management', 'real estate brokerage',
                    'mortgage lending', 'mortgage', 'realty', 'rental',
                    'short term rental', 'airbnb'],
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
                            'cleaning', 'janitorial', 'handyman', 'contractor',
                            'renovation', 'remodeling', 'carpentry', 'masonry'],
    'hospitality': ['hotel', 'motel', 'inn', 'lodging', 'hostel',
                    'bed and breakfast', 'event', 'entertainment',
                    'nightclub', 'lounge', 'banquet'],
    'transportation': ['transportation', 'delivery', 'courier', 'moving',
                       'trucking', 'logistics', 'shipping', 'taxi', 'limo',
                       'rideshare'],
}


def load_and_prepare_data(filepath):
    '''Load the DBA CSV and engineer features for modeling'''
    df = pd.read_csv(filepath)

    # parse dates
    df['Date of Filing'] = pd.to_datetime(df['Date of Filing'], errors='coerce')
    df['Date of Expiration'] = pd.to_datetime(df['Date of Expiration'], errors='coerce')
    df['Last Renewal Date'] = pd.to_datetime(df['Last Renewal Date'], errors='coerce')

    # target: is the business expired?
    today = pd.Timestamp.today()
    df['is_expired'] = (df['Date of Expiration'] < today).astype(int)

    # feature: business age in years
    df['age_years'] = (today - df['Date of Filing']).dt.days / 365.25

    # feature: was the business ever renewed?
    df['was_renewed'] = df['Last Renewal Date'].notna().astype(int)

    # feature: neighborhood from zip
    zip_to_neighborhood = {}
    for neighborhood, zips in ZIPS_BY_NEIGHBORHOOD.items():
        for z in zips:
            zip_to_neighborhood[z] = neighborhood
    df['neighborhood'] = df['Zipcode'].map(zip_to_neighborhood)

    # feature: business category from type
    df['biz_type_clean'] = df['Type of Business'].fillna('unknown').str.strip().str.lower()
    df['business_category'] = df['biz_type_clean'].apply(categorize_business)

    # GPS features (if lat/lon columns exist)
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['lat'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['lon'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])

        # distance to nearest MBTA stop
        mbta_stops = fetch_mbta_stops()
        if mbta_stops is not None:
            df['dist_to_mbta'] = df.apply(
                lambda row: min_distance_to_stops(row['lat'], row['lon'], mbta_stops),
                axis=1
            )

        # number of other businesses within ~200m (~0.002 degrees)
        df['nearby_businesses'] = count_nearby(df, radius_deg=0.002)

    # drop rows with missing critical values
    df = df.dropna(subset=['neighborhood', 'age_years', 'is_expired'])

    return df


def haversine_km(lat1, lon1, lat2, lon2):
    '''Distance in km between two GPS points'''
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def fetch_mbta_stops():
    '''Fetch MBTA subway/light rail stop coordinates'''
    try:
        url = 'https://api-v3.mbta.com/stops?filter[route_type]=0,1'
        response = requests.get(url, timeout=10)
        data = response.json()
        stops = [(s['attributes']['latitude'], s['attributes']['longitude'])
                 for s in data['data']]
        print(f'  Fetched {len(stops)} MBTA stops')
        return stops
    except Exception as e:
        print(f'  Warning: could not fetch MBTA stops ({e}), skipping distance feature')
        return None


def min_distance_to_stops(lat, lon, stops):
    '''Distance in km from a point to the nearest MBTA stop'''
    distances = [haversine_km(lat, lon, s[0], s[1]) for s in stops]
    return min(distances)


def count_nearby(df, radius_deg=0.002):
    '''Count businesses within radius_deg (~200m) of each business'''
    lats = df['lat'].values
    lons = df['lon'].values
    counts = np.zeros(len(df), dtype=int)
    for i in range(len(df)):
        dists = np.sqrt((lats - lats[i])**2 + (lons - lons[i])**2)
        counts[i] = (dists < radius_deg).sum() - 1  # exclude self
    return counts


def categorize_business(biz_type):
    '''Map a raw business type string to a broader category'''
    for category, keywords in BUSINESS_CATEGORIES.items():
        for keyword in keywords:
            if keyword in biz_type:
                return category
    return 'other'


def prepare_features(df):
    '''Encode categorical features and return X, y arrays'''
    # encode categoricals
    le_neighborhood = LabelEncoder()
    le_category = LabelEncoder()

    df = df.copy()
    df['neighborhood_enc'] = le_neighborhood.fit_transform(df['neighborhood'])
    df['category_enc'] = le_category.fit_transform(df['business_category'])

    feature_cols = ['neighborhood_enc', 'category_enc', 'age_years', 'was_renewed']
    X = df[feature_cols].values
    y = df['is_expired'].values

    feature_names = ['Neighborhood', 'Business Category', 'Age (years)', 'Was Renewed']

    return X, y, feature_names, le_neighborhood, le_category


def train_and_evaluate(X_train, X_test, y_train, y_test, feature_names):
    '''Train multiple models and compare performance'''
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
        'KNN (k=5)': KNeighborsClassifier(n_neighbors=5),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            'model': model,
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1': f1,
            'confusion_matrix': cm,
            'y_pred': y_pred,
        }

        print(f'\n{"="*50}')
        print(f'{name}')
        print(f'{"="*50}')
        print(f'Accuracy:  {acc:.4f}')
        print(f'Precision: {prec:.4f}')
        print(f'Recall:    {rec:.4f}')
        print(f'F1 Score:  {f1:.4f}')
        print(f'\nClassification Report:')
        print(classification_report(y_test, y_pred,
                                    target_names=['Active', 'Expired']))

    return results


def plot_confusion_matrices(results, y_test):
    '''Plot confusion matrix for each model'''
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for idx, (name, res) in enumerate(results.items()):
        ConfusionMatrixDisplay(
            confusion_matrix=res['confusion_matrix'],
            display_labels=['Active', 'Expired']
        ).plot(ax=axes[idx], cmap='Blues', colorbar=False)
        axes[idx].set_title(f'{name}')

    plt.suptitle('Confusion Matrices — Business Expiration Prediction', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrices.png'), dpi=150)
    print('\nSaved: outputs/confusion_matrices.png')
    plt.close()


def plot_model_comparison(results):
    '''Bar chart comparing model metrics'''
    model_names = list(results.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score']

    x = np.arange(len(model_names))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
        values = [results[m][metric] for m in model_names]
        ax.bar(x + i * width, values, width, label=label)

    ax.set_ylabel('Score')
    ax.set_title('Model Comparison — Business Expiration Prediction')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(model_names, rotation=15, ha='right')
    ax.legend()
    ax.set_ylim(0, 1)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'model_comparison.png'), dpi=150)
    print('Saved: outputs/model_comparison.png')
    plt.close()


def plot_feature_importance(results, feature_names):
    '''Plot feature importance from the Random Forest model'''
    rf_model = results['Random Forest']['model']
    importances = rf_model.feature_importances_

    fig, ax = plt.subplots(figsize=(8, 5))
    sorted_idx = np.argsort(importances)
    ax.barh(range(len(sorted_idx)), importances[sorted_idx], color='steelblue')
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels([feature_names[i] for i in sorted_idx])
    ax.set_xlabel('Feature Importance')
    ax.set_title('Random Forest — Feature Importance')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'feature_importance.png'), dpi=150)
    print('Saved: outputs/feature_importance.png')
    plt.close()


def plot_expiration_by_neighborhood(df):
    '''Stacked bar chart: active vs expired by neighborhood'''
    ct = pd.crosstab(df['neighborhood'], df['is_expired'])
    ct.columns = ['Active', 'Expired']
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ct.plot(kind='bar', stacked=True, color=['steelblue', 'coral'], ax=axes[0])
    axes[0].set_title('Business Count by Neighborhood')
    axes[0].set_ylabel('Number of Businesses')
    axes[0].set_xlabel('')
    axes[0].tick_params(axis='x', rotation=45)

    ct_pct.plot(kind='bar', stacked=True, color=['steelblue', 'coral'], ax=axes[1])
    axes[1].set_title('Expiration Rate by Neighborhood')
    axes[1].set_ylabel('Percentage')
    axes[1].set_xlabel('')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].legend(loc='lower right')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'expiration_by_neighborhood.png'), dpi=150)
    print('Saved: outputs/expiration_by_neighborhood.png')
    plt.close()


def plot_expiration_by_category(df):
    '''Horizontal bar chart: expiration rate by business category'''
    ct = pd.crosstab(df['business_category'], df['is_expired'])
    ct.columns = ['Active', 'Expired']
    ct['total'] = ct.sum(axis=1)
    ct['expiration_rate'] = ct['Expired'] / ct['total'] * 100

    # only show categories with at least 20 businesses
    ct = ct[ct['total'] >= 20].sort_values('expiration_rate')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(ct.index, ct['expiration_rate'], color='coral')
    ax.set_xlabel('Expiration Rate (%)')
    ax.set_title('Business Expiration Rate by Category (min 20 businesses)')
    ax.axvline(x=ct['expiration_rate'].mean(), color='gray', linestyle='--',
               label=f'Mean: {ct["expiration_rate"].mean():.1f}%')
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'expiration_by_category.png'), dpi=150)
    print('Saved: outputs/expiration_by_category.png')
    plt.close()


def cross_validate_best_model(X, y, results):
    '''Run 5-fold cross validation on the best model'''
    best_name = max(results, key=lambda k: results[k]['f1'])
    best_model = results[best_name]['model']

    cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='f1')
    print(f'\n{"="*50}')
    print(f'5-Fold Cross Validation — {best_name}')
    print(f'{"="*50}')
    print(f'F1 scores per fold: {cv_scores.round(4)}')
    print(f'Mean F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})')

    return best_name, cv_scores


# =========================================================================
# PART 2: Entrepreneur Model — only uses features known BEFORE opening
# =========================================================================

def prepare_entrepreneur_features(df):
    '''
    Only use neighborhood + business category as features.
    These are the decisions an entrepreneur makes before opening.
    No age, no renewal — those would be data leakage.
    '''
    le_neighborhood = LabelEncoder()
    le_category = LabelEncoder()

    df = df.copy()
    df['neighborhood_enc'] = le_neighborhood.fit_transform(df['neighborhood'])
    df['category_enc'] = le_category.fit_transform(df['business_category'])

    X = df[['neighborhood_enc', 'category_enc']].values
    y = df['is_expired'].values
    feature_names = ['Neighborhood', 'Business Category']

    return X, y, feature_names, le_neighborhood, le_category


def run_entrepreneur_model(df):
    '''Classification using only pre-opening decision features'''
    print(f'\n{"#"*60}')
    print(f'PART 2: ENTREPRENEUR MODEL (Neighborhood + Business Type Only)')
    print(f'{"#"*60}')
    print('Features: Neighborhood, Business Category')
    print('(No age or renewal — simulates a new business decision)\n')

    X, y, feat_names, le_n, le_c = prepare_entrepreneur_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results = train_and_evaluate(X_train, X_test, y_train, y_test, feat_names)

    # confusion matrices for entrepreneur model
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    for idx, (name, res) in enumerate(results.items()):
        ConfusionMatrixDisplay(
            confusion_matrix=res['confusion_matrix'],
            display_labels=['Active', 'Expired']
        ).plot(ax=axes[idx], cmap='Greens', colorbar=False)
        axes[idx].set_title(f'{name}')
    plt.suptitle('Entrepreneur Model — Confusion Matrices\n(Neighborhood + Business Type Only)', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'entrepreneur_confusion_matrices.png'), dpi=150)
    print('\nSaved: outputs/entrepreneur_confusion_matrices.png')
    plt.close()

    # success rate heatmap: neighborhood x category
    plot_success_heatmap(df)

    return results


def plot_success_heatmap(df):
    '''Heatmap showing survival rate by neighborhood x business category'''
    # only categories with enough data
    cat_counts = df['business_category'].value_counts()
    top_cats = cat_counts[cat_counts >= 30].index

    subset = df[df['business_category'].isin(top_cats)]
    survival = subset.groupby(['neighborhood', 'business_category'])['is_expired'].apply(
        lambda x: (1 - x.mean()) * 100
    ).unstack(fill_value=np.nan)

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(survival, annot=True, fmt='.0f', cmap='RdYlGn', center=70,
                linewidths=0.5, ax=ax, cbar_kws={'label': 'Survival Rate (%)'})
    ax.set_title('Business Survival Rate (%) by Neighborhood and Category')
    ax.set_ylabel('Neighborhood')
    ax.set_xlabel('Business Category')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'survival_heatmap.png'), dpi=150)
    print('Saved: outputs/survival_heatmap.png')
    plt.close()


# =========================================================================
# PART 3: Longevity Regression — predict how long a business will last
# =========================================================================

def run_longevity_regression(df):
    '''Predict business age (longevity) from neighborhood + type'''
    print(f'\n{"#"*60}')
    print(f'PART 3: LONGEVITY REGRESSION')
    print(f'{"#"*60}')
    print('Target: business age (years)')
    print('Features: Neighborhood, Business Category\n')

    le_n = LabelEncoder()
    le_c = LabelEncoder()
    df = df.copy()
    df['neighborhood_enc'] = le_n.fit_transform(df['neighborhood'])
    df['category_enc'] = le_c.fit_transform(df['business_category'])

    X = df[['neighborhood_enc', 'category_enc']].values
    y = df['age_years'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        'Linear Regression': LinearRegression(),
        'Decision Tree': DecisionTreeRegressor(max_depth=5, random_state=42),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
        'KNN (k=5)': KNeighborsRegressor(n_neighbors=5),
    }

    reg_results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        reg_results[name] = {'r2': r2, 'mae': mae, 'rmse': rmse, 'model': model}

        print(f'\n{"="*50}')
        print(f'{name}')
        print(f'{"="*50}')
        print(f'R² Score: {r2:.4f}')
        print(f'MAE:      {mae:.4f} years')
        print(f'RMSE:     {rmse:.4f} years')

    # plot regression comparison
    fig, ax = plt.subplots(figsize=(10, 5))
    names = list(reg_results.keys())
    r2_vals = [reg_results[n]['r2'] for n in names]
    mae_vals = [reg_results[n]['mae'] for n in names]

    x = np.arange(len(names))
    width = 0.35
    ax.bar(x - width/2, r2_vals, width, label='R² Score', color='steelblue')
    ax.bar(x + width/2, mae_vals, width, label='MAE (years)', color='coral')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha='right')
    ax.set_title('Longevity Regression — Model Comparison')
    ax.legend()
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'longevity_regression_comparison.png'), dpi=150)
    print('\nSaved: outputs/longevity_regression_comparison.png')
    plt.close()

    # predicted vs actual scatter for best model
    best_name = max(reg_results, key=lambda k: reg_results[k]['r2'])
    best_pred = reg_results[best_name]['model'].predict(X_test)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_test, best_pred, alpha=0.3, s=10, color='steelblue')
    ax.plot([0, y_test.max()], [0, y_test.max()], 'r--', label='Perfect prediction')
    ax.set_xlabel('Actual Age (years)')
    ax.set_ylabel('Predicted Age (years)')
    ax.set_title(f'{best_name} — Predicted vs Actual Business Longevity')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'longevity_predicted_vs_actual.png'), dpi=150)
    print('Saved: outputs/longevity_predicted_vs_actual.png')
    plt.close()

    # average predicted longevity by neighborhood
    plot_predicted_longevity(df, reg_results, le_n, le_c)

    return reg_results


def plot_predicted_longevity(df, reg_results, le_n, le_c):
    '''Bar chart: average longevity by neighborhood, actual vs predicted'''
    best_name = max(reg_results, key=lambda k: reg_results[k]['r2'])
    model = reg_results[best_name]['model']

    avg_actual = df.groupby('neighborhood')['age_years'].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    avg_actual.plot(kind='bar', color='steelblue', ax=ax)
    ax.set_ylabel('Average Business Age (years)')
    ax.set_title('Average Business Longevity by Neighborhood')
    ax.set_xlabel('')

    for i, (neigh, val) in enumerate(avg_actual.items()):
        ax.text(i, val + 0.1, f'{val:.1f}', ha='center', va='bottom', fontsize=10)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'avg_longevity_by_neighborhood.png'), dpi=150)
    print('Saved: outputs/avg_longevity_by_neighborhood.png')
    plt.close()


# =========================================================================
# PART 4: K-Means Clustering — geographic business clusters
# =========================================================================

def run_kmeans_clustering(df):
    '''Cluster businesses by GPS location and analyze survival by cluster'''
    if 'lat' not in df.columns or 'lon' not in df.columns:
        print('\nSkipping K-Means: no GPS data available')
        return None

    print(f'\n{"#"*60}')
    print(f'PART 4: K-MEANS CLUSTERING (GPS-based)')
    print(f'{"#"*60}')

    coords = df[['lat', 'lon']].values

    # find optimal k using silhouette score
    k_range = range(3, 11)
    silhouettes = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(coords)
        sil = silhouette_score(coords, labels)
        silhouettes.append(sil)
        print(f'  k={k}: silhouette={sil:.4f}')

    best_k = list(k_range)[np.argmax(silhouettes)]
    print(f'\n  Best k={best_k} (silhouette={max(silhouettes):.4f})')

    # plot silhouette scores
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(list(k_range), silhouettes, 'o-', color='steelblue')
    ax.set_xlabel('Number of Clusters (k)')
    ax.set_ylabel('Silhouette Score')
    ax.set_title('K-Means — Optimal Cluster Count')
    ax.axvline(x=best_k, color='coral', linestyle='--', label=f'Best k={best_k}')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'kmeans_silhouette.png'), dpi=150)
    print('Saved: outputs/kmeans_silhouette.png')
    plt.close()

    # fit with best k
    km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df = df.copy()
    df['cluster'] = km.fit_predict(coords)

    # plot clusters on map with survival coloring
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # left: colored by cluster
    scatter = axes[0].scatter(df['lon'], df['lat'], c=df['cluster'], cmap='tab10',
                              alpha=0.5, s=8)
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    axes[0].set_title(f'Business Clusters (k={best_k})')
    plt.colorbar(scatter, ax=axes[0], label='Cluster')

    # right: colored by survival
    colors = df['is_expired'].map({0: 'steelblue', 1: 'coral'})
    axes[1].scatter(df['lon'], df['lat'], c=colors, alpha=0.5, s=8)
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    axes[1].set_title('Business Locations (Blue=Active, Red=Expired)')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'kmeans_map.png'), dpi=150)
    print('Saved: outputs/kmeans_map.png')
    plt.close()

    # survival rate by cluster
    cluster_stats = df.groupby('cluster').agg(
        count=('is_expired', 'size'),
        expired=('is_expired', 'sum'),
        survival_rate=('is_expired', lambda x: (1 - x.mean()) * 100),
        avg_age=('age_years', 'mean'),
        avg_nearby=('nearby_businesses', 'mean') if 'nearby_businesses' in df.columns else ('age_years', 'mean'),
    ).round(1)
    print(f'\nCluster Statistics:')
    print(cluster_stats)

    # bar chart of survival by cluster
    fig, ax = plt.subplots(figsize=(10, 5))
    cluster_stats['survival_rate'].plot(kind='bar', color='steelblue', ax=ax)
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Survival Rate (%)')
    ax.set_title('Business Survival Rate by Geographic Cluster')
    ax.axhline(y=(1 - df['is_expired'].mean()) * 100, color='coral', linestyle='--',
               label=f'Overall: {(1 - df["is_expired"].mean()) * 100:.1f}%')
    ax.legend()
    for i, v in enumerate(cluster_stats['survival_rate']):
        ax.text(i, v + 0.5, f'{v:.0f}%', ha='center', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'survival_by_cluster.png'), dpi=150)
    print('Saved: outputs/survival_by_cluster.png')
    plt.close()

    # density vs survival scatter
    if 'nearby_businesses' in df.columns:
        density_survival = df.groupby(
            pd.cut(df['nearby_businesses'], bins=10)
        )['is_expired'].apply(lambda x: (1 - x.mean()) * 100)

        fig, ax = plt.subplots(figsize=(10, 5))
        density_survival.plot(kind='bar', color='steelblue', ax=ax)
        ax.set_xlabel('Number of Nearby Businesses (within ~200m)')
        ax.set_ylabel('Survival Rate (%)')
        ax.set_title('Business Density vs Survival Rate')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'density_vs_survival.png'), dpi=150)
        print('Saved: outputs/density_vs_survival.png')
        plt.close()

    return df, best_k


# =========================================================================
# PART 5: Spatial Model — entrepreneur model enhanced with GPS features
# =========================================================================

def run_spatial_model(df):
    '''Classification using neighborhood + type + GPS-derived features'''
    has_mbta = 'dist_to_mbta' in df.columns
    has_nearby = 'nearby_businesses' in df.columns

    if not has_nearby:
        print('\nSkipping Spatial Model: no GPS features available')
        return None

    print(f'\n{"#"*60}')
    print(f'PART 5: SPATIAL MODEL (Location + Type + GPS Features)')
    print(f'{"#"*60}')

    le_n = LabelEncoder()
    le_c = LabelEncoder()
    df = df.copy()
    df['neighborhood_enc'] = le_n.fit_transform(df['neighborhood'])
    df['category_enc'] = le_c.fit_transform(df['business_category'])

    feature_cols = ['neighborhood_enc', 'category_enc', 'nearby_businesses']
    feature_names = ['Neighborhood', 'Business Category', 'Nearby Businesses']

    if has_mbta:
        feature_cols.append('dist_to_mbta')
        feature_names.append('Distance to MBTA (km)')

    X = df[feature_cols].values
    y = df['is_expired'].values

    print(f'Features: {feature_names}')
    print(f'(Entrepreneur model + GPS spatial features, still no data leakage)\n')

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results = train_and_evaluate(X_train, X_test, y_train, y_test, feature_names)

    # feature importance
    rf = results['Random Forest']['model']
    importances = rf.feature_importances_
    fig, ax = plt.subplots(figsize=(8, 5))
    sorted_idx = np.argsort(importances)
    ax.barh(range(len(sorted_idx)), importances[sorted_idx], color='steelblue')
    ax.set_yticks(range(len(sorted_idx)))
    ax.set_yticklabels([feature_names[i] for i in sorted_idx])
    ax.set_xlabel('Feature Importance')
    ax.set_title('Spatial Model — Feature Importance')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'spatial_feature_importance.png'), dpi=150)
    print('Saved: outputs/spatial_feature_importance.png')
    plt.close()

    # confusion matrices
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    for idx, (name, res) in enumerate(results.items()):
        ConfusionMatrixDisplay(
            confusion_matrix=res['confusion_matrix'],
            display_labels=['Active', 'Expired']
        ).plot(ax=axes[idx], cmap='Purples', colorbar=False)
        axes[idx].set_title(f'{name}')
    plt.suptitle('Spatial Model — Confusion Matrices\n(Neighborhood + Type + GPS Features)', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'spatial_confusion_matrices.png'), dpi=150)
    print('Saved: outputs/spatial_confusion_matrices.png')
    plt.close()

    return results


def main():
    filepath = '../CityofBoston-CityClerkDBA_cleaned.csv'

    # =====================================================================
    # PART 1: Full Classification Model (all features)
    # =====================================================================
    print(f'{"#"*60}')
    print(f'PART 1: FULL CLASSIFICATION MODEL')
    print(f'{"#"*60}')
    print('Loading and preparing data...')
    df = load_and_prepare_data(filepath)

    print(f'\nDataset: {len(df)} businesses')
    print(f'Target distribution:')
    print(f'  Active:  {(df["is_expired"] == 0).sum()} ({(df["is_expired"] == 0).mean():.1%})')
    print(f'  Expired: {(df["is_expired"] == 1).sum()} ({(df["is_expired"] == 1).mean():.1%})')
    print(f'\nNeighborhoods: {df["neighborhood"].nunique()}')
    print(df['neighborhood'].value_counts())
    print(f'\nBusiness categories: {df["business_category"].nunique()}')
    print(df['business_category'].value_counts())

    # prepare features and split
    X, y, feature_names, le_neigh, le_cat = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f'\nTrain: {len(X_train)}, Test: {len(X_test)}')

    # train and evaluate
    results = train_and_evaluate(X_train, X_test, y_train, y_test, feature_names)

    # visualizations
    plot_confusion_matrices(results, y_test)
    plot_model_comparison(results)
    plot_feature_importance(results, feature_names)
    plot_expiration_by_neighborhood(df)
    plot_expiration_by_category(df)

    # cross validation on best model
    best_name, cv_scores = cross_validate_best_model(X, y, results)

    # =====================================================================
    # PART 2: Entrepreneur Model (no data leakage)
    # =====================================================================
    ent_results = run_entrepreneur_model(df)

    # =====================================================================
    # PART 3: Longevity Regression
    # =====================================================================
    reg_results = run_longevity_regression(df)

    # =====================================================================
    # PART 4: K-Means Clustering
    # =====================================================================
    cluster_result = run_kmeans_clustering(df)
    if cluster_result is not None:
        df_clustered, best_k = cluster_result

    # =====================================================================
    # PART 5: Spatial Model (entrepreneur + GPS features)
    # =====================================================================
    spatial_results = run_spatial_model(df)

    # =====================================================================
    # FINAL SUMMARY
    # =====================================================================
    print(f'\n{"#"*60}')
    print(f'FINAL SUMMARY')
    print(f'{"#"*60}')
    print(f'\nPart 1 — Full Classification (all features):')
    print(f'  Best model: {best_name} (CV F1: {cv_scores.mean():.4f})')
    print(f'  Features: {feature_names}')

    ent_best = max(ent_results, key=lambda k: ent_results[k]['f1'])
    print(f'\nPart 2 — Entrepreneur Model (location + type only):')
    print(f'  Best model: {ent_best}')
    print(f'  Accuracy: {ent_results[ent_best]["accuracy"]:.4f}')
    print(f'  F1: {ent_results[ent_best]["f1"]:.4f}')

    reg_best = max(reg_results, key=lambda k: reg_results[k]['r2'])
    print(f'\nPart 3 — Longevity Regression:')
    print(f'  Best model: {reg_best}')
    print(f'  R²: {reg_results[reg_best]["r2"]:.4f}')
    print(f'  MAE: {reg_results[reg_best]["mae"]:.2f} years')

    if cluster_result is not None:
        print(f'\nPart 4 — K-Means Clustering:')
        print(f'  Optimal clusters: {best_k}')

    if spatial_results is not None:
        sp_best = max(spatial_results, key=lambda k: spatial_results[k]['f1'])
        print(f'\nPart 5 — Spatial Model (entrepreneur + GPS):')
        print(f'  Best model: {sp_best}')
        print(f'  Accuracy: {spatial_results[sp_best]["accuracy"]:.4f}')
        print(f'  F1: {spatial_results[sp_best]["f1"]:.4f}')
        print(f'  (vs Entrepreneur model F1: {ent_results[ent_best]["f1"]:.4f})')

    print(f'\nAll plots saved in outputs/ directory.')


if __name__ == '__main__':
    main()
