
import pandas as pd

INPUT_FILE = "mens_t20_data/recent_completed_matches.csv"
OUTPUT_FILE = "mens_t20_data/t20_recent_results.csv"

df = pd.read_csv(INPUT_FILE)

# Handle missing values
for col in ["competition", "home", "away"]:
    df[col] = df[col].fillna("")


def is_t20(competition):
    competition = str(competition).lower()

    excluded = [
        "sixes",
        "pro50",
        "odi",
        "one-day",
        "one day",
        "first class",
        "ranji",
        "t10",
        "test",
        "presidents trophy",
        "challenge league a"
    ]

    if any(word in competition for word in excluded):
        return False

    return "t20" in competition or "gt20" in competition


def get_category(row):
    competition = str(row["competition"]).lower()
    home = str(row["home"]).lower()
    away = str(row["away"]).lower()

    combined = f"{competition} {home} {away}"

    if "women" in combined or "woman" in combined:
        return "Women's T20"

    return "Men's T20"


# Keep T20 competitions
t20_matches = df[
    df["competition"].apply(is_t20)
].copy()

# Identify category
t20_matches["match_category"] = t20_matches.apply(
    get_category, axis=1
)

# Remove duplicates
t20_matches = t20_matches.drop_duplicates(
    subset=["home", "away", "time"]
)

# Save results
t20_matches.to_csv(OUTPUT_FILE, index=False)

print("\nMen's and Women's T20 Completed Matches")
print("=" * 55)

print("\nCategory Summary:")
print(t20_matches["match_category"].value_counts().to_string())

print("\nCompetition Summary:")
print(t20_matches["competition"].value_counts().to_string())

print("\nTotal T20 Matches:", len(t20_matches))
print("Filtered results saved to:", OUTPUT_FILE)
