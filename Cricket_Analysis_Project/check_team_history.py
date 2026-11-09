
import pandas as pd

df = pd.read_csv(
    "mens_t20_data/prepared_recent_results.csv"
)

# Count matches played by each team
team_counts = pd.concat([
    df["home"],
    df["away"]
]).value_counts()

# Teams with at least 3 matches
experienced_teams = team_counts[team_counts >= 3]

print("\nTOTAL UNIQUE TEAMS:", len(team_counts))

print("\nTEAMS WITH AT LEAST 3 MATCHES:")
print(experienced_teams.to_string())

print("\nTOTAL TEAMS WITH AT LEAST 3 MATCHES:")
print(len(experienced_teams))

# Keep matches where both teams have at least 3 appearances
filtered = df[
    df["home"].isin(experienced_teams.index) &
    df["away"].isin(experienced_teams.index)
].copy()

print("\nMATCHES BETWEEN THESE TEAMS:")
print(len(filtered))

print("\nSAVED DATASET:")
filtered.to_csv(
    "mens_t20_data/experienced_teams_matches.csv",
    index=False
)

print("mens_t20_data/experienced_teams_matches.csv")
