import pandas as pd

import preprocessing_licenses
import preprocessing_DBA_latandlong
import preprocessing_combining
import shared
import build_businesstypes
import eda_plotting
import hypothesis04_test
import modeling

def main():
    preprocessing_licenses.main()
    preprocessing_DBA_latandlong.main()
    build_businesstypes.build()
    eda_plotting.main()
    # Lazy import: hypothesis_diversity reads data at module level, so it must be imported AFTER the cleaned CSV has been written above.
    import hypothesis_diversity
    hypothesis_diversity.main()
    hypothesis04_test.main()
    modeling.main()

if __name__ == '__main__':
    main()
