import requests
import pandas as pd
# Create API variables
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
    Get 
    '''
    response = requests.get(API).json()
    stops_data = [stop['attributes'] for stop in response['data']]
    df = pd.DataFrame(stops_data)
    print(df.columns.tolist())

    gps_coords = df[['name', 'latitude', 'longitude']]
    print(gps_coords)
    print(df['name'].nunique())

def main():
    API = create_API_variables()
    call_API_load(API)

if __name__ == '__main__':
    main()