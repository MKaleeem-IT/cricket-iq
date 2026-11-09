import requests
import pandas as pd
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "live_scores.csv"

# API key (environment variable se lo, ya direct daalo)
API_KEY = os.environ.get("CRICAPI_KEY", "125ff309-38e9-40e7-a58b-1e3251af1bfa")


def fetch_live_scores():
    if not API_KEY or API_KEY == "YOUR_CRICAPI_KEY_HERE":
        print("❌ API key missing.")
        return

    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            print(f"⚠️ API error: {data.get('reason', 'unknown')}")
            # Empty file with header
            df = pd.DataFrame(
                columns=["home", "away", "score_team1", "score_team2", "status"]
            )
            DATA_DIR.mkdir(exist_ok=True)
            df.to_csv(OUTPUT_FILE, index=False)
            return

        matches = data.get("data", [])
        if not matches:
            print("⚠️ No matches found from API.")
            df = pd.DataFrame(
                columns=["home", "away", "score_team1", "score_team2", "status"]
            )
            DATA_DIR.mkdir(exist_ok=True)
            df.to_csv(OUTPUT_FILE, index=False)
            return

        rows = []
        for m in matches:
            # Sirf T20 matches
            match_type = str(m.get("matchType", "")).upper()
            if "T20" not in match_type:
                continue

            # 👇 FIX: Sirf LIVE matches (started but NOT ended)
            if not m.get("matchStarted"):
                continue
            if m.get("matchEnded"):
                continue

            teams = m.get("teams", [])
            if len(teams) < 2:
                continue

            team1 = teams[0]
            team2 = teams[1]

            # -------------------------------------------------
            # Score parse karo
            # -------------------------------------------------
            score_data = m.get("score", [])
            score_team1 = ""
            score_team2 = ""

            for s in score_data:
                inning_name = str(s.get("inning", ""))
                runs = s.get("r", 0)
                wickets = s.get("w", 0)
                overs = s.get("o", 0)
                score_str = f"{runs}/{wickets} ({overs} ov)"

                inning_lower = inning_name.lower()
                t1_lower = team1.lower()
                t2_lower = team2.lower()

                if t1_lower in inning_lower:
                    score_team1 = score_str
                elif t2_lower in inning_lower:
                    score_team2 = score_str

            # Agar score empty hai, to bhi include karo (status se pata chalega)
            rows.append({
                "home": team1,
                "away": team2,
                "score_team1": score_team1,
                "score_team2": score_team2,
                "status": m.get("status", "")
            })

        if not rows:
            print("⚠️ No live T20 matches found right now.")
            df = pd.DataFrame(
                columns=["home", "away", "score_team1", "score_team2", "status"]
            )
        else:
            df = pd.DataFrame(rows)

        DATA_DIR.mkdir(exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Live scores saved: {len(df)} matches")

        if len(df) > 0:
            print("\nLive Matches:")
            print(df.to_string(index=False))

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    fetch_live_scores()