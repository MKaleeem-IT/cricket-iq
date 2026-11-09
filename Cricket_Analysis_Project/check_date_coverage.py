
import pandas as pd

df = pd.read_csv(
    "mens_t20_data/prepared_recent_results.csv"
)

df["time"] = pd.to_datetime(
    df["time"],
    errors="coerce",
    utc=True
)

print("\nEARLIEST MATCH:")
print(df["time"].min())

print("\nLATEST MATCH:")
print(df["time"].max())

print("\nMATCHES BY MONTH:")
print(
    df["time"]
    .dt.to_period("M")
    .value_counts()
    .sort_index()
)

print("\nTOTAL MATCHES:")
print(len(df))
