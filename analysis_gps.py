import pandas as pd
import numpy as np

import fetch_foodanddrink as licences
import fetch_mbtaAPI as mbta


def analyze_gps():
    API = create_API_variables()
    call_API_load(API)

if __name__ == '__main__':
    main()