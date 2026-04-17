import pandas as pd

ZIPS_BY_NEIGHBORHOOD = {

}
'''
Shared constants and functions used across preprocessing, EDA, and
hypothesis testing.
'''
from pathlib import Path

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

def calculate_age(df, filing_col, expiration_col):
    df[filing_col] = pd.to_datetime(df[filing_col], errors='coerce')
    df[expiration_col] = pd.to_datetime(df[expiration_col], errors='coerce')
    df = df.dropna(subset=[filing_col, expiration_col])
    df["age"] = (df[expiration_col] - df[filing_col]).dt.days
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
