
import pandas as pd
import re
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "t20_recent_results.csv"
OUTPUT_FILE = BASE_DIR / "prepared_recent_results.csv"


# Previously verified official results
# Key format: (date, sorted team names)
verified_results = {
    ("2026-10-25", ("Rocks", "Titans")): "Rocks",
    ("2026-10-08", ("Easterns", "Rocks")): "Rocks",
    ("2026-08-22", ("Gold Coast", "Wynnum Manly")): "Draw",
    ("2026-07-06", ("Derbyshire", "Lancashire")): "Draw",
    ("2026-07-02", ("Portugal", "Sweden")): "Portugal",
}


def extract_runs(score):
    """Extract the leading run total from a score string."""
    if pd.isna(score):
        return None

    match = re.match(r"^\s*(\d+)", str(score))

    if match:
        return int(match.group(1))

    return None


def get_date(value):
    """Convert match time to YYYY-MM-DD."""
    date = pd.to_datetime(value, errors="coerce", utc=True)

    if pd.isna(date):
        return None

    return date.strftime("%Y-%m-%d")


def main():
    print("Loading recent T20 matches...")

    if not INPUT_FILE.exists():
        print("ERROR: Input file not found:", INPUT_FILE)
        return

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "home", "away", "home_score", "away_score",
        "time", "competition", "match_category"
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        print("ERROR: Missing columns:", missing)
        return

    print("Total input matches:", len(df))

    prepared = []
    missing_scores = 0
    unverified_equal_scores = []

    for _, row in df.iterrows():
        home_runs = extract_runs(row["home_score"])
        away_runs = extract_runs(row["away_score"])

        if home_runs is None or away_runs is None:
            missing_scores += 1
            continue

        date = get_date(row["time"])

        if date is None:
            continue

        home = str(row["home"]).strip()
        away = str(row["away"]).strip()

        teams = tuple(sorted([home, away]))
        result_key = (date, teams)

        if result_key in verified_results:
            winner = verified_results[result_key]
            winner_source = "verified_official"

            if winner == "Draw":
                result = "Match drawn"
            else:
                result = "Won"

        elif home_runs == away_runs:
            unverified_equal_scores.append(
                f"{date}: {home} vs {away}"
            )
            continue

        else:
            winner = home if home_runs > away_runs else away
            winner_source = "score_inferred"
            result = "Won"

        prepared.append({
            "time": row["time"],
            "home": home,
            "away": away,
            "home_score": row["home_score"],
            "away_score": row["away_score"],
            "home_runs": home_runs,
            "away_runs": away_runs,
            "winner": winner,
            "result": result,
            "competition": row["competition"],
            "match_category": row["match_category"],
            "winner_source": winner_source
        })

    result_df = pd.DataFrame(prepared)

    result_df.to_csv(OUTPUT_FILE, index=False)

    print("\nPreparation completed!")
    print("Valid matches:", len(result_df))
    print("Matches excluded due to missing scores:", missing_scores)
    print("Unverified equal-score matches excluded:", len(unverified_equal_scores))

    if unverified_equal_scores:
        print("\nEqual-score matches needing verification:")
        for match in unverified_equal_scores:
            print("-", match)

    if not result_df.empty:
        print("\nCategory summary:")
        print(result_df["match_category"].value_counts())

        print("\nResult summary:")
        print(result_df["result"].value_counts())

        print("\nWinner source summary:")
        print(result_df["winner_source"].value_counts())

    print("\nSaved file:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
