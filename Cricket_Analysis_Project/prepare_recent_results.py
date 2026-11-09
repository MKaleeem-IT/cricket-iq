
import pandas as pd
import re

INPUT_FILE = "mens_t20_data/t20_recent_results.csv"
OUTPUT_FILE = "mens_t20_data/prepared_recent_results.csv"

df = pd.read_csv(INPUT_FILE)

print("Total T20 records loaded:", len(df))


def get_runs(score):
    if pd.isna(score):
        return None

    match = re.match(r"^\s*(\d+)", str(score))

    return int(match.group(1)) if match else None


def normalize(value):
    return str(value).strip().lower()


def match_key(home, away, match_time):
    date = str(match_time)[:10]
    teams = tuple(sorted([normalize(home), normalize(away)]))
    return date, teams


# Official results verified from match scorecards.
# The team names are matched without depending on home/away order.
verified_results = {
    ("2026-10-25", ("rocks", "titans")): {
        "winner": "Rocks",
        "result": "Won",
    },
    ("2026-10-08", ("easterns", "rocks")): {
        "winner": "Rocks",
        "result": "Won",
    },
    ("2026-08-22", ("gold coast", "wynnum manly")): {
        "winner": "Draw",
        "result": "Match drawn",
    },
    ("2026-07-06", ("derbyshire", "lancashire")): {
        "winner": "Draw",
        "result": "Match drawn",
    },
    ("2026-07-02", ("portugal", "sweden")): {
        "winner": "Portugal",
        "result": "Won",
    },
}


df["home_runs"] = df["home_score"].apply(get_runs)
df["away_runs"] = df["away_score"].apply(get_runs)

valid = df[
    df["home_runs"].notna() &
    df["away_runs"].notna()
].copy()

if "match_category" not in valid.columns:
    valid["match_category"] = "Unknown"


prepared_rows = []
excluded_equal_scores = 0

for _, row in valid.iterrows():

    key = match_key(row["home"], row["away"], row["time"])

    # First use an officially verified result.
    if key in verified_results:
        official = verified_results[key]

        row["winner"] = official["winner"]
        row["result"] = official["result"]
        row["winner_source"] = "verified_official"

    # Otherwise, infer the result only when runs differ.
    elif row["home_runs"] > row["away_runs"]:
        row["winner"] = row["home"]
        row["result"] = "Won"
        row["winner_source"] = "score_inferred"

    elif row["away_runs"] > row["home_runs"]:
        row["winner"] = row["away"]
        row["result"] = "Won"
        row["winner_source"] = "score_inferred"

    # Equal scores without verified official results are excluded.
    else:
        excluded_equal_scores += 1
        continue

    prepared_rows.append(row)


prepared = pd.DataFrame(prepared_rows)

prepared = prepared.drop_duplicates(
    subset=["home", "away", "time", "competition"]
)

prepared.to_csv(OUTPUT_FILE, index=False)


print("\nPrepared Men's and Women's T20 Results")
print("=" * 55)

print("\nCategory Summary:")
print(prepared["match_category"].value_counts().to_string())

print("\nResult Summary:")
print(prepared["result"].value_counts().to_string())

print("\nWinner Source Summary:")
print(prepared["winner_source"].value_counts().to_string())

print("\nVerified Official Results:")
print(
    prepared[prepared["winner_source"] == "verified_official"][
        ["home", "away", "competition", "home_score",
         "away_score", "winner", "result"]
    ].to_string(index=False)
)

print("\nSample Prepared Results:")
print(
    prepared[
        ["home", "away", "competition", "match_category",
         "home_score", "away_score", "winner", "winner_source"]
    ].head(15).to_string(index=False)
)

print("\nTotal Valid Matches:", len(prepared))
print("Unverified equal-score matches excluded:", excluded_equal_scores)
print("Saved:", OUTPUT_FILE)

print("\nIMPORTANT:")
print("Unequal-score results are inferred from scores.")
print("DLS and other exceptional results may need separate verification.")
