import requests
import pandas as pd
import os
# Scrape MBTA API data and make a dataframe
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
    Create a DF from API string
    '''
    response = requests.get(API).json()
    stops_data = [stop['attributes'] for stop in response['data']]
    df = pd.DataFrame(stops_data)
    print(df.columns.tolist())

    gps_coords = df[['name', 'latitude', 'longitude']]
    #print(df['name'].nunique())
    return gps_coords

def main():
    if os.path.exists('data/MBTA_stops.csv'):
        return pd.read_csv('data/MBTA_stops.csv')
    API = create_API_variables()
    return call_API_load(API)

if __name__ == '__main__':
    gps_coords = main()
    print(gps_coords)
    