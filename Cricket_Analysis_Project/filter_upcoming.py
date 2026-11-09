
import pandas as pd

# File paths
INPUT_FILE = "data/upcoming_fixtures.csv"
OUTPUT_FILE = "data/mens_t20_upcoming.csv"

# Read upcoming fixtures
df = pd.read_csv(INPUT_FILE)

# Handle missing values
for col in ["competition", "home", "away"]:
    df[col] = df[col].fillna("")

# Exclude non-T20 formats
excluded_words = [
    "sixes",
    "pro50",
    "50 over",
    "one day",
    "odi",
    "test"
]

def is_excluded(row):
    competition = str(row["competition"]).lower()
    home = str(row["home"]).lower()
    away = str(row["away"]).lower()

    combined = f"{competition} {home} {away}"
    return any(word in combined for word in excluded_words)


def is_t20(competition):
    competition = str(competition).lower()
    return "t20" in competition or "gt20" in competition


# Filter Men's and Women's T20 fixtures
t20_matches = df[
    (~df.apply(is_excluded, axis=1)) &
    (df["competition"].apply(is_t20))
].copy()

# Remove duplicate fixtures
t20_matches = t20_matches.drop_duplicates(
    subset=["home", "away", "time"]
)

# Keep consistent columns
columns = [
    "home", "away", "competition",
    "time", "status", "status_text", "url"
]

t20_matches = t20_matches.reindex(columns=columns)

# Save output
t20_matches.to_csv(OUTPUT_FILE, index=False)

# Display results
print("\nUpcoming Men's and Women's T20 Matches")
print("=" * 55)

if not t20_matches.empty:
    print(
        t20_matches[
            ["home", "away", "competition", "time"]
        ].to_string(index=False)
    )
else:
    print("No upcoming T20 fixtures found.")

print("\nTotal Upcoming T20 Matches:", len(t20_matches))
print("Filtered data saved successfully.")
