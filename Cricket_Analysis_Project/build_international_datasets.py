
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Correct T20-only folders
MEN_DIR = DATA_DIR / "international_t20" / "mens_t20_only"
WOMEN_DIR = DATA_DIR / "international_t20" / "womens_t20_only"


def get_match_data(file_path, category):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        info = data.get("info", {})

        # IMPORTANT: Exclude ODI, Test and other formats
        if info.get("match_type") != "T20":
            return None

        outcome = info.get("outcome", {})
        teams = info.get("teams", [])
        dates = info.get("dates", [])

        if len(teams) != 2:
            print(f"Skipping invalid team data: {file_path.name}")
            return None

        # Official winner and result
        winner = outcome.get("winner")

        if not winner:
            if outcome.get("result") == "tie":
                winner = "Tie"
            elif outcome.get("result") == "draw":
                winner = "Draw"
            elif outcome.get("result") == "no result":
                winner = "No Result"
            elif outcome.get("eliminator"):
                winner = outcome.get("eliminator")

        # Extract innings scores
        scores = {}

        for inning in data.get("innings", []):
            team = inning.get("team", "Unknown")
            total_runs = 0

            for over in inning.get("overs", []):
                for delivery in over.get("deliveries", []):
                    runs = delivery.get("runs", {})
                    total_runs += runs.get("total", 0)

            scores[team] = scores.get(team, 0) + total_runs

        return {
            "match_id": file_path.stem,
            "date": dates[0] if dates else None,
            "category": category,
            "team1": teams[0],
            "team2": teams[1],
            "winner": winner,
            "result": outcome.get("result", "normal"),
            "venue": info.get("venue"),
            "city": info.get("city"),
            "event": info.get("event", {}).get("name"),
            "team1_score": scores.get(teams[0]),
            "team2_score": scores.get(teams[1]),
            "source_file": file_path.name
        }

    except Exception as error:
        print(f"Error reading {file_path.name}: {error}")
        return None


def build_dataset(folder, category, output_file):

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    files = sorted(folder.rglob("*.json"))

    print(f"\nProcessing {category}...")
    print(f"JSON files found: {len(files)}")

    records = []

    for file_path in files:
        record = get_match_data(file_path, category)

        if record is not None:
            records.append(record)

    df = pd.DataFrame(records)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.drop_duplicates(subset=["match_id"])
        df = df.sort_values("date").reset_index(drop=True)

    output_path = DATA_DIR / output_file
    df.to_csv(output_path, index=False)

    print(f"T20 matches extracted: {len(df)}")
    print(f"Missing winners: {df['winner'].isna().sum() if not df.empty else 0}")
    print(f"Saved to: {output_path}")

    return df


if __name__ == "__main__":

    men_df = build_dataset(
        MEN_DIR,
        "Men's T20",
        "mens_international_t20.csv"
    )

    women_df = build_dataset(
        WOMEN_DIR,
        "Women's T20",
        "womens_international_t20.csv"
    )

    print("\n========== DATASET SUMMARY ==========")
    print(f"Men's T20 matches: {len(men_df)}")
    print(f"Women's T20 matches: {len(women_df)}")
    print(f"Total T20 matches: {len(men_df) + len(women_df)}")

    print("\nMen's tournament breakdown:")
    if not men_df.empty:
        print(men_df["event"].value_counts().to_string())

    print("\nWomen's tournament breakdown:")
    if not women_df.empty:
        print(women_df["event"].value_counts().to_string())

    print("\nDataset creation completed successfully.")
