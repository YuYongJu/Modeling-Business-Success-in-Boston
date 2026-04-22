'''
Shared constants and functions used across preprocessing, EDA, and
hypothesis testing.
'''
import pandas as pd
from pathlib import Path

MAPTILER_API_KEY = ''

_REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = _REPO_ROOT / 'data' / 'businesstypes.csv'


ZIPS_BY_NEIGHBORHOOD = {
    'Allston/Brighton': [2134, 2135, 2163],
    'Back Bay': [2116, 2117, 2199, 2216, 2217, 2295],
    'Beacon Hill': [2108, 2123, 2133],
    'Charlestown': [2129],
    'Chinatown/Downtown': [2111],
    'Downtown/Financial District': [2109, 2110],
    'Dorchester': [2122, 2124, 2125],
    'East Boston': [2128, 2228],
    'Fenway/Kenmore': [2115, 2215],
    'Government Center/West End': [2101, 2102, 2103, 2104, 2105, 2106, 2107, 2113, 2114, 2196],
    'Hyde Park': [2136],
    'Jamaica Plain': [2130],
    'Mattapan': [2126],
    'North End': [2112],
    'Roslindale': [2131],
    'Roxbury': [2119, 2120, 2121],
    'South Boston': [2127],
    'Seaport': [2210],
    'South End': [2118],
    'West Roxbury': [2132]
}

# flat zip -> neighborhood lookup
ZIP_TO_NEIGHBORHOOD = {
    z: n for n, zips in ZIPS_BY_NEIGHBORHOOD.items() for z in zips
}

def categorize_business_type(btype):
    '''
    Lowercase, strip, and map a business type string to a broader category.
    '''
    if btype != btype:
        return 'Other'
    btype = str(btype).lower().strip()

    if ('restaurant' in btype or 'food' in btype or 'pub' in btype
            or 'cafe' in btype or 'coffee' in btype or 'pizza' in btype
            or 'bakery' in btype):
        return 'Food & Drink'
    if ('supermarket' in btype or 'grocery' in btype or 'convenience' in btype
            or 'liquor' in btype or 'market' in btype):
        return 'Grocery & Convenience'
    if ('beauty' in btype or 'hair' in btype or 'salon' in btype
            or 'barber' in btype or 'spa' in btype or 'nail' in btype
            or 'massage' in btype or 'fitness' in btype
            or 'cosmetics' in btype or 'sport' in btype):
        return 'Beauty & Personal Care'
    if ('real estate' in btype or 'property' in btype
            or 'mortgage' in btype or 'rental' in btype):
        return 'Real Estate'
    if ('cleaning' in btype or 'landscaping' in btype
            or 'construction' in btype or 'contractor' in btype):
        return 'Trades & Services'
    if ('dentist' in btype or 'doctor' in btype or 'medical' in btype
            or 'health' in btype or 'clinic' in btype):
        return 'Health & Medical'
    if ('transport' in btype or 'uber' in btype or 'lyft' in btype
            or 'livery' in btype or 'taxi' in btype or 'towing' in btype):
        return 'Transportation'
    if ('photo' in btype or 'entertaiment' in btype or 'art' in btype
            or 'event' in btype or 'music' in btype or 'studio' in btype):
        return 'Arts & Entertainment'
    if ('retail' in btype or 'store' in btype or 'shop' in btype
            or 'boutique' in btype or 'jewelry' in btype
            or 'florist' in btype or 'flower' in btype
            or 'home improvement' in btype):
        return 'Retail'
    return 'Other'


def encode_neighborhoods(df, zip_col):
    '''
    Add a 'neighborhood' column based on zip code.
    Rows with unrecognized zips get NaN.
    '''
    zip_to_neighborhood = {
        z: n for n, zips in ZIPS_BY_NEIGHBORHOOD.items() for z in zips
    }
    df[zip_col] = pd.to_numeric(df[zip_col], errors='coerce')
    df['neighborhood'] = df[zip_col].map(zip_to_neighborhood)
    return df

def calculate_distance(gps1, gps2):
    '''
    Calculate Manhattan distance (city blocks) between two gps coordinates.
    Attributes:
        gps1: tuple of (latitude, longitude) for first location
        gps2: tuple of (latitude, longitude) for second location
    Returns:
        Distance in meters between the two locations
    '''
    lat1, lon1 = gps1
    lat2, lon2 = gps2

    distance = ((lat1 - lat2) + (lon1 - lon2)) * 111111  # Approximate conversion to kilometers

    return distance

def calc_age(df, filing_col, expiration_col):
    '''
    Calculate age and active status for each business.
    Attributes: dataframe
    Returns: dataframe with two new columns:
        is_active: True if expiration date is in the future.
        age_years: for active businesses, today - date of filing.
                for closed businesses, date of expiration - date of filing.
    '''
    today = pd.Timestamp.today()
    df[filing_col] = pd.to_datetime(df[filing_col], errors="coerce", format="mixed")
    df[expiration_col] = pd.to_datetime(df[expiration_col], errors="coerce", format="mixed")
    df = df.dropna(subset=[filing_col, expiration_col])

    df["is_active"] = df[expiration_col] > today
    end_date = df[expiration_col].where(~df["is_active"], other=today)
    df["age_years"] = (end_date - df[filing_col]).dt.days / 365
    
    return df

def create_API_variables():
    '''
    Makes the api key string.
    filtering for Subway (1) and Light Rail (0)
    '''
    baseUrl = 'https://api-v3.mbta.com/'
    endpoint = 'stops'
    filters = '?filter[route_type]=0,1'
    API = f'{baseUrl}{endpoint}{filters}'
    return API

def call_API_load(API):
    '''
    Create a DF from API string.
    Attributes: API string
    Returns: DataFrame with columns 'name', 'latitude', 'longitude' for each stop
    '''
    response = requests.get(API).json()
    stops_data = [stop['attributes'] for stop in response['data']]
    df = pd.DataFrame(stops_data)
    print(df.columns.tolist())

    gps_coords = df[['name', 'latitude', 'longitude']]
    return gps_coords

def fetch_mbtaAPI():
    '''
    Fetch MBTA stop data from API, or load from local file if it exists.
    Attributes: None
    Returns: DataFrame with columns 'name', 'latitude', 'longitude' for each stop
    '''
    if os.path.exists('data/MBTA_stops.csv'):
        return pd.read_csv('data/MBTA_stops.csv')
    API = create_API_variables()
    df = call_API_load(API)
    df.to_csv('data/MBTA_stops.csv', index=False)
    return df
    
def find_remove_outliers(df):
    before = len(df)
    df = df[
        (df["latitude"] >= 41) & (df["latitude"] <= 43) &
        (df["longitude"] >= -72) & (df["longitude"] <= -70)
    ]
    after = len(df)
    print(f"Removed {before - after} outliers based on latitude and longitude ({after} remaining)")
    return df

def add_distance_to_stops():
    pass

def add_chain_count():
    pass


def normalize_name(df, name_col):
    df["business_name_normalized"] = df[name_col].apply(
        lambda name: ''.join(char for char in str(name).lower() if char.isalnum() or char.isspace())
        .replace("inc", "").replace("llc", "").strip())
    return df
