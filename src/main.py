import pandas as pd

import preprocessing_licenses
import preprocessing_DBA_latandlong
import preprocessing_combining
import shared
import eda_plotting
import hypothesis_diversity
import hypothesis04_test
import modeling

def main():
    preprocessing_licenses.main()
    preprocessing_DBA_latandlong.main()
    eda_plotting.main()
    hypothesis_diversity.main()
    hypothesis04_test.main()
    modeling.main()

if __name__ == '__main__':
    main()