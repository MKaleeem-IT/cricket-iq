
import pandas as pd

# STEP 1: LOAD CLEANED DATASET
df = pd.read_csv("data/cleaned_cricket_matches.csv")

print("Cleaned Dataset Loaded Successfully!")
print("Original Shape:", df.shape)

# STEP 2: EXTRACT YEAR
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

# STEP 3: CHECK WINNER VALUES
# Every winner must be either team1 or team2

valid_winners = (
    (df["winner"] == df["team1"]) |
    (df["winner"] == df["team2"])
)

if not valid_winners.all():
    print("Some winner values do not match the participating teams.")
    print(df.loc[~valid_winners, ["team1", "team2", "winner"]])
    raise ValueError("Please investigate these matches before continuing.")

# STEP 4: CREATE TARGET COLUMN
# 1 = Team 1 won
# 0 = Team 2 won

df["team1_won"] = (
    df["winner"] == df["team1"]
).astype(int)

# STEP 5: SELECT INPUT FEATURES AND TARGET

features = [
    "team1",
    "team2",
    "city",
    "venue",
    "toss_winner",
    "toss_decision",
    "year"
]

target = "team1_won"

ml_df = df[features + [target]].copy()

# STEP 6: CHECK THE ML DATASET

print("\nML Dataset:")
print(ml_df.head())

print("\nML Dataset Shape:")
print(ml_df.shape)

print("\nMissing Values:")
print(ml_df.isnull().sum())

print("\nTarget Distribution:")
print(ml_df[target].value_counts())

print("\nTarget Meaning:")
print("1 = Team 1 Wins")
print("0 = Team 2 Wins")

# STEP 7: SAVE ML DATASET

ml_df.to_csv(
    "data/ml_dataset.csv",
    index=False
)

print("\nML Dataset Created Successfully!")
