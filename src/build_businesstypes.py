'''
Build data/businesstypes.csv from the tracked cleaned DBA file.

Downstream scripts (modeling.py, hypothesis04_test.py) expect a CSV at
data/businesstypes.csv with three engineered columns that the raw City
Clerk file doesn't carry: is_active, neighborhood, business_type_clean.
This script produces that file so teammates can run the analysis from a
fresh clone without needing a MapTiler API key.

Input:  data/CityofBoston-CityClerkDBA_cleaned.csv
    The cleaned DBA file, which already has geocoded latitude/longitude
    columns. We do not re-run geocoding here because that step requires
    a paid MapTiler API key and is handled separately by
    preprocessing_DBA_latandlong.py.

Derived columns:
    is_active            True if Date of Expiration is in the future.
    neighborhood         Zipcode mapped via shared.ZIP_TO_NEIGHBORHOOD.
    business_type_clean  Lowercased, stripped Type of Business.

Output: data/businesstypes.csv

Usage:
    python src/build_businesstypes.py        # from repo root
'''
import pandas as pd
from pathlib import Path

from shared import ZIP_TO_NEIGHBORHOOD

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / 'data' / 'CityofBoston-CityClerkDBA_cleaned.csv'
OUTPUT_FILE = ROOT / 'data' / 'businesstypes.csv'


def build():
    '''Read the cleaned DBA CSV, derive three columns, and write the output.

    Parameters
        None. Reads from INPUT_FILE (data/CityofBoston-CityClerkDBA_cleaned.csv)
        and writes to OUTPUT_FILE (data/businesstypes.csv).

    Returns
        None. Side effects:
            - Writes data/businesstypes.csv with three added columns:
              is_active (bool), neighborhood (str), business_type_clean (str).
            - Prints a summary to stdout (rows written, active/closed split,
              mapped/unmapped neighborhoods, geocoded count) so a teammate
              running this from a fresh clone can sanity-check the result.
        Raises FileNotFoundError if INPUT_FILE is missing.

    Assumptions
        - INPUT_FILE must contain columns: 'Date of Expiration', 'Zipcode',
          'Type of Business', 'latitude', 'longitude'.
        - 'Date of Expiration' strings that fail parsing are coerced to NaT,
          which makes is_active=False for those rows (NaT > today is False).
        - Zipcodes not present in shared.ZIP_TO_NEIGHBORHOOD yield NaN
          neighborhood — expected for out-of-Boston or malformed zips and
          reported in the summary line.
        - `is_active` is computed at run time, so the output file's active
          counts shift slightly every day licenses expire — re-run before
          analysis if freshness matters.
    '''
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f'Missing input file: {INPUT_FILE.relative_to(ROOT)}. '
            f'This file is tracked in git; try `git pull` or check your clone.')

    df = pd.read_csv(INPUT_FILE)

    df['Date of Expiration'] = pd.to_datetime(
        df['Date of Expiration'], errors='coerce')
    today = pd.Timestamp.today()
    df['is_active'] = df['Date of Expiration'] > today

    df['Zipcode'] = pd.to_numeric(df['Zipcode'], errors='coerce')
    df['neighborhood'] = df['Zipcode'].map(ZIP_TO_NEIGHBORHOOD)

    df['business_type_clean'] = (df['Type of Business']
                                 .astype(str).str.lower().str.strip())

    df.to_csv(OUTPUT_FILE, index=False)
    print(f'Wrote {len(df)} rows -> {OUTPUT_FILE.relative_to(ROOT)}')
    print(f'  is_active:    {int(df["is_active"].sum())} active, '
          f'{int((~df["is_active"]).sum())} closed')
    print(f'  neighborhood: {int(df["neighborhood"].notna().sum())} mapped, '
          f'{int(df["neighborhood"].isna().sum())} unmapped (missing/out-of-Boston zip)')
    print(f'  geocoded:     {int(df[["latitude", "longitude"]].notna().all(axis=1).sum())} '
          f'rows with lat/lon')


if __name__ == '__main__':
    build()
