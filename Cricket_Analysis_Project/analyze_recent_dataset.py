
import pandas as pd

df = pd.read_csv(
    "mens_t20_data/prepared_recent_results.csv"
)

print("\nTOTAL MATCHES:")
print(len(df))

print("\nMATCHES BY COMPETITION:")
print(df["competition"].value_counts().to_string())

print("\nUNIQUE TEAMS:")
teams = sorted(set(df["home"].dropna()) | set(df["away"].dropna()))

for team in teams:
    print(team)

print("\nTOTAL UNIQUE TEAMS:")
print(len(teams))

print("\nMATCHES PER TEAM:")
team_counts = pd.concat([
    df["home"],
    df["away"]
]).value_counts()

print(team_counts.to_string())
