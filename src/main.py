import pandas as pd

import preprocessing_licenses
import preprocessing_DBA_latandlong
import preprocessing_combining
import shared
import build_businesstypes
import eda_plotting
import eda_alcohol_licenses
import hypothesis04_test
import modeling

def main():
    preprocessing_licenses.main()
    preprocessing_DBA_latandlong.main()
    build_businesstypes.build()
    eda_plotting.main()
    eda_alcohol_licenses.main()
    import hypothesis_diversity
    hypothesis_diversity.main()
    hypothesis04_test.main()
    modeling.main()

if __name__ == '__main__':
    main()
