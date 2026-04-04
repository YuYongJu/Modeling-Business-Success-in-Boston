# Business age by neighborhood

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('CityofBoston-CityClerkDBA.csv')

print(df.columns.tolist())
print(df.head(5))

# parse the data
