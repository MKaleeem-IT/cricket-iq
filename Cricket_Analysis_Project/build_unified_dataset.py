
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Source files
recent_file = BASE_DIR / "mens_t20_data" / "prepared_recent_results.csv"
mens_file = BASE_DIR / "data" / "mens_international_t20.csv"
womens_file = BASE_DIR / "data" / "womens_international_t20.csv"

# Output file
output_file = BASE_DIR / "data" / "unified_t20_history.csv"


def prepare_recent(df):
    data = pd.DataFrame({
        "date": pd.to_datetime(df["time"], utc=True, errors="coerce"),
        "team1": df["home"],
        "team2": df["away"],
        "winner": df["winner"],
        "result": df["result"],
        "category": df["match_category"],
        "team1_score": df["home_runs"],
        "team2_score": df["away_runs"],
        "competition": df["competition"],
        "venue": None,
        "city": None,
        "source_type": "recent_results",
        "winner_source": df["winner_source"]
    })

    return data


def prepare_international(df):
    data = pd.DataFrame({
        "date": pd.to_datetime(df["date"], errors="coerce", utc=True),
        "team1": df["team1"],
        "team2": df["team2"],
        "winner": df["winner"],
        "result": df["result"],
        "category": df["category"],
        "team1_score": df["team1_score"],
        "team2_score": df["team2_score"],
        "competition": df["event"],
        "venue": df["venue"],
        "city": df["city"],
        "source_type": "international_dataset",
        "winner_source": "international_dataset"
    })

    return data


# Load source datasets
recent = pd.read_csv(recent_file)
mens = pd.read_csv(mens_file)
womens = pd.read_csv(womens_file)

# Prepare records
recent_data = prepare_recent(recent)
mens_data = prepare_international(mens)
womens_data = prepare_international(womens)

# Combine datasets
unified = pd.concat(
    [recent_data, mens_data, womens_data],
    ignore_index=True
)

# Clean team names and categories
for col in ["team1", "team2", "winner", "category", "competition"]:
    unified[col] = unified[col].astype("string").str.strip()

# Remove invalid dates and incomplete team records
unified = unified.dropna(
    subset=["date", "team1", "team2", "category"]
)

# Remove duplicate matches within the combined dataset.
# Keep the recent source if the same fixture is present in both.
unified["date_key"] = unified["date"].dt.strftime("%Y-%m-%d")
unified["team_key"] = unified.apply(
    lambda row: "|".join(sorted([
        str(row["team1"]).casefold(),
        str(row["team2"]).casefold()
    ])),
    axis=1
)

unified = unified.sort_values(
    by="source_type",
    key=lambda col: col.map({
        "recent_results": 0,
        "international_dataset": 1
    })
)

unified = unified.drop_duplicates(
    subset=["date_key", "team_key", "category", "competition"],
    keep="first"
)

unified = unified.drop(columns=["date_key", "team_key"])

# Sort chronologically
unified = unified.sort_values("date").reset_index(drop=True)

# Save
unified.to_csv(output_file, index=False)

print("\nUNIFIED T20 DATASET CREATED")
print("=" * 45)
print("Total matches:", len(unified))
print("\nCategory breakdown:")
print(unified["category"].value_counts())

print("\nSource breakdown:")
print(pd.crosstab(unified["category"], unified["source_type"]))

print("\nWinner source breakdown:")
print(unified["winner_source"].value_counts())

print("\nMissing values:")
print(unified.isnull().sum())

print("\nSaved to:", output_file)
