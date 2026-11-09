
import os
import json
import pandas as pd

# STEP 1: DATASET FOLDER
data_folder = "data/icc_mens_t20_world_cup_male_json"

# Store match information
matches = []

# STEP 2: READ ALL JSON FILES
for filename in os.listdir(data_folder):

    if filename.endswith(".json"):

        file_path = os.path.join(data_folder, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            match_data = json.load(file)

        info = match_data["info"]
        outcome = info.get("outcome", {})

        # Extract important match information
        match = {
            "match_id": filename,
            "date": info["dates"][0],
            "city": info.get("city"),
            "venue": info.get("venue"),
            "team1": info["teams"][0],
            "team2": info["teams"][1],
            "toss_winner": info["toss"]["winner"],
            "toss_decision": info["toss"]["decision"],
            "winner": outcome.get("winner"),
            "result": outcome.get("result"),
            "eliminator": outcome.get("eliminator")
        }

        matches.append(match)

# STEP 3: CONVERT INTO DATAFRAME
df = pd.DataFrame(matches)

print("\nDataset Created Successfully!")

# STEP 4: UNDERSTAND THE DATASET
print("\nFirst Five Matches:")
print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nDataset Dimensions:")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\nColumn Names:")
print(df.columns.tolist())

print("\nColumn Information:")
df.info()

print("\nStatistical Summary:")
print(df.describe(include="all"))

# STEP 5: CHECK DATA QUALITY
print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Matches:")
print(df.duplicated().sum())

print("\nData Types:")
print(df.dtypes)

# STEP 6: INVESTIGATE MISSING VALUES
print("\nMatches with Missing City:")
print(df[df["city"].isnull()])

print("\nMatches with Missing Winner:")
print(df[df["winner"].isnull()])

# STEP 7: CHECK WINNER CATEGORIES
print("\nWinner Categories:")
print(df["winner"].value_counts(dropna=False))

# STEP 8: INVESTIGATE MATCHES WITHOUT WINNERS
print("\nInvestigating Missing Match Results:")

for filename in os.listdir(data_folder):

    if filename.endswith(".json"):

        file_path = os.path.join(data_folder, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            match_data = json.load(file)

        outcome = match_data["info"].get("outcome", {})

        if not outcome.get("winner"):

            print("\nMatch File:", filename)
            print("Teams:", match_data["info"]["teams"])
            print("Outcome:", outcome)

# STEP 9: DATA PREPROCESSING
clean_df = df.copy()

# Convert date into datetime format
clean_df["date"] = pd.to_datetime(clean_df["date"])

print("\nDate Data Type:")
print(clean_df["date"].dtype)

print("\nMissing Values Before Cleaning:")
print(clean_df.isnull().sum())

# STEP 10: HANDLE TIED MATCHES
# Use eliminator winner when regular winner is missing
clean_df["winner"] = clean_df["winner"].fillna(
    clean_df["eliminator"]
)

# STEP 11: REMOVE MATCHES WITHOUT A WINNER
# Remove no-result matches
clean_df = clean_df[
    clean_df["winner"].notna()
].copy()

# Reset row numbers
clean_df = clean_df.reset_index(drop=True)

# STEP 12: HANDLE MISSING CITY VALUES
# Fill missing city where venue identifies Sylhet
missing_city = clean_df["city"].isnull()

clean_df.loc[
    missing_city & clean_df["venue"].str.contains(
        "Sylhet", case=False, na=False
    ),
    "city"
] = "Sylhet"

# STEP 13: CHECK CLEANED DATASET
print("\nDataset After Cleaning:")
print(clean_df.shape)

print("\nMissing Values After Cleaning:")
print(clean_df.isnull().sum())

print("\nWinner Categories After Cleaning:")
print(clean_df["winner"].value_counts())

print("\nMissing City Values After Cleaning:")
print(clean_df["city"].isnull().sum())

print("\nFirst Five Cleaned Matches:")
print(clean_df.head())

# STEP 14: SAVE CLEANED DATASET
clean_df.to_csv(
    "data/cleaned_cricket_matches.csv",
    index=False
)

print("\nCleaned Dataset Saved Successfully!")
