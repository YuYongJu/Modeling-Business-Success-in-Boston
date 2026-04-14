'''
Shared constants and functions used across preprocessing, EDA, and
hypothesis testing.
'''
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = _REPO_ROOT / 'data' / 'businesstypes.csv'


ZIPS_BY_NEIGHBORHOOD = {
    'Allston/Brighton': [2134, 2135, 2163],
    'Back Bay/Beacon Hill': [2108, 2116, 2117, 2123, 2133, 2199, 2216, 2217, 2295],
    'Central Boston': [2101, 2102, 2103, 2104, 2105, 2106, 2107, 2109, 2110, 2111, 2112, 2113, 2114, 2196, 2201, 2202, 2203, 2204, 2205, 2206, 2207, 2208, 2209, 2211, 2212, 2222, 2293],
    'Charlestown': [2129],
    'Dorchester': [2122, 2124, 2125],
    'East Boston': [2128, 2228],
    'Fenway/Kenmore': [2115, 2215],
    'Hyde Park': [2136],
    'Jamaica Plain': [2130],
    'Mattapan': [2126],
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
    '''Map a cleaned business_type string to a broader category.

    Expects btype to already be lowercased and stripped.
    '''
    if btype != btype:
        return 'Other'
    if ('restaurant' in btype or 'food' in btype or 'pub' in btype
            or 'cafe' in btype or 'coffee' in btype or 'pizza' in btype
            or 'bakery' in btype):
        return 'Food & Drink'
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
            or 'florist' in btype or 'flower' in btype):
        return 'Retail'
    return 'Other'


def encode_neighborhoods():
    pass


def calculate_distance():
    pass


def add_distance_to_stops():
    pass


def add_chain_count():
    pass


def normalize_name(df, name_col):
    df["business_name_normalized"] = df[name_col].apply(
        lambda name: ''.join(char for char in str(name).lower() if char.isalnum() or char.isspace())
        .replace("inc", "").replace("llc", "").strip())
    return df
