import pandas as pd

df = pd.read_csv("mens_t20_data/prepared_recent_results.csv")

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nData Types:")
print(df.dtypes)

print("\nFirst 5 Records:")
print(df.head())