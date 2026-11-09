
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

JSON_DIR = DATA_DIR / "icc_mens_t20_world_cup_male_json"
OUTPUT_FILE = DATA_DIR / "cleaned_cricket_matches.csv"


def create_updated_dataset():

    matches = []

    json_files = list(JSON_DIR.rglob("*.json"))

    print(f"Reading {len(json_files)} JSON files...")

    for file_path in json_files:

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        info = data.get("info", {})

        teams = info.get("teams", [])

        if len(teams) != 2:
            continue

        toss = info.get("toss", {})
        outcome = info.get("outcome", {})

        winner = outcome.get("winner")
        result = outcome.get("by", {})

        eliminator = outcome.get("eliminator")

        city = info.get("city")
        venue = info.get("venue")

        if not city and venue and "Sylhet" in venue:
            city = "Sylhet"

        match = {
            "match_id": file_path.stem,
            "date": info.get("dates", [None])[0],
            "city": city,
            "venue": venue,
            "team1": teams[0],
            "team2": teams[1],
            "toss_winner": toss.get("winner"),
            "toss_decision": toss.get("decision"),
            "winner": winner,
            "result": next(iter(result.keys()), None),
            "eliminator": eliminator
        }

        # Handle tied matches
        if not winner and eliminator in teams:
            match["winner"] = eliminator

        # Skip matches without a confirmed winner
        if not match["winner"]:
            continue

        matches.append(match)

    df = pd.DataFrame(matches)

    df["date"] = pd.to_datetime(df["date"])

    df = df.drop_duplicates(subset="match_id")

    df = df.sort_values("date").reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nUpdated dataset created successfully!")
    print("Total matches:", len(df))
    print("Missing values:")
    print(df.isnull().sum())
    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    create_updated_dataset()
