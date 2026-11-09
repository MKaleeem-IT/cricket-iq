
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned dataset
df = pd.read_csv("data/cleaned_cricket_matches.csv")

# STEP 1: CHECK DATASET
print("Dataset Loaded Successfully!")
print("Dataset Shape:", df.shape)

# STEP 2: TOP WINNING TEAMS
team_wins = df["winner"].value_counts()

print("\nTop Winning Teams:")
print(team_wins.head(10))

# STEP 3: VISUALIZE TOP 10 WINNING TEAMS
plt.figure(figsize=(12, 6))

sns.barplot(
    x=team_wins.head(10).values,
    y=team_wins.head(10).index
)

plt.title("Top 10 Teams by Match Wins")
plt.xlabel("Number of Wins")
plt.ylabel("Teams")
plt.tight_layout()

plt.savefig("top_winning_teams.png")
plt.show()
# STEP 4: TOSS DECISION VS MATCH OUTCOME

df["toss_winner_won"] = (
    df["toss_winner"] == df["winner"]
)

toss_analysis = pd.crosstab(
    df["toss_decision"],
    df["toss_winner_won"]
)

toss_analysis.columns = [
    "Lost Match",
    "Won Match"
]

print("\nToss Decision vs Match Outcome:")
print(toss_analysis)

# Create graph
toss_analysis.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.title("Toss Decision vs Match Outcome")
plt.xlabel("Toss Decision")
plt.ylabel("Number of Matches")
plt.xticks(rotation=0)
plt.legend(title="Toss Winner Result")
plt.tight_layout()

plt.savefig("toss_decision_analysis.png")
plt.show()
# STEP 5: MATCHES PLAYED IN EACH CITY

city_matches = df["city"].value_counts().head(10)

print("\nTop 10 Cities by Matches Hosted:")
print(city_matches)

plt.figure(figsize=(12, 6))

sns.barplot(
    x=city_matches.values,
    y=city_matches.index
)

plt.title("Top 10 Cities by Matches Hosted")
plt.xlabel("Number of Matches")
plt.ylabel("Cities")

plt.tight_layout()
plt.savefig("top_cities.png")
plt.show()
# STEP 6: MATCHES PLAYED PER YEAR

df["date"] = pd.to_datetime(df["date"])

df["year"] = df["date"].dt.year

year_matches = df["year"].value_counts().sort_index()

print("\nMatches Played Per Year:")
print(year_matches)

plt.figure(figsize=(12, 6))

sns.barplot(
    x=year_matches.index,
    y=year_matches.values
)

plt.title("Number of Matches Played Per Year")
plt.xlabel("Year")
plt.ylabel("Number of Matches")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("matches_per_year.png")
plt.show()