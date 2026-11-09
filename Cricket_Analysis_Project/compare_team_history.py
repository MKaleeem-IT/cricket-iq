
import pandas as pd

# Load datasets
international = pd.read_csv("data/mens_international_t20.csv")
recent = pd.read_csv("mens_t20_data/prepared_recent_results.csv")

# Keep men's recent matches only
recent = recent[recent["match_category"] == "Men's T20"]

# Get international team names
teams = sorted(
    set(international["team1"].dropna()) |
    set(international["team2"].dropna())
)

print("\nMEN'S TEAM HISTORY COMPARISON")
print("=" * 65)
print(f"{'TEAM':30} {'INTERNATIONAL':>15} {'RECENT':>10}")
print("-" * 65)

for team in teams:
    international_count = (
        (international["team1"] == team) |
        (international["team2"] == team)
    ).sum()

    recent_count = (
        (recent["home"] == team) |
        (recent["away"] == team)
    ).sum()

    if recent_count > 0:
        print(
            f"{team:30} "
            f"{international_count:15} "
            f"{recent_count:10}"
        )

print("\nComparison completed.")
