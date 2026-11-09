import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
import os

# Project directory
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

OUTPUT_FILE = DATA_DIR / "mens_t20_upcoming.csv"

# 👇 API key environment variable se lo, ya directly yahan daalo
API_KEY = os.environ.get("CRICAPI_KEY", "125ff309-38e9-40e7-a58b-1e3251af1bfa")


def fetch_fixtures():

    if not API_KEY or API_KEY == "YOUR_CRICAPI_KEY_HERE":
        print("❌ API key missing. Set CRICAPI_KEY environment variable or edit API_KEY in code.")
        return

    # CricAPI endpoints
    # currentMatches: live + recent matches
    # matches: all matches (includes upcoming)
    urls = [
        f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0",
        f"https://api.cricapi.com/v1/matches?apikey={API_KEY}&offset=0",
    ]

    all_matches = []

    for url in urls:
        try:
            print(f"Fetching: {url.split('/')[-1].split('?')[0]}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "success":
                print(f"  ⚠️  API error: {data.get('reason', 'unknown')}")
                continue

            matches = data.get("data", [])
            all_matches.extend(matches)
            print(f"  ✅ Found {len(matches)} matches")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    if not all_matches:
        print("\n⚠️  No matches found from API.")
        df = pd.DataFrame(columns=[
            "home", "away", "competition", "time",
            "status", "status_text", "url"
        ])
        DATA_DIR.mkdir(exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)
        return

    # -----------------------------------------------------
    # Parse T20 matches only
    # -----------------------------------------------------
    rows = []
    for m in all_matches:
        # Skip ended matches
        if m.get("matchEnded"):
            continue

        # Only T20
        match_type = str(m.get("matchType", "")).upper()
        if "T20" not in match_type:
            continue

        teams = m.get("teams", [])
        if len(teams) < 2:
            continue

        # Get date/time
        date_str = m.get("dateTimeGMT") or m.get("date", "")
        if not date_str:
            continue

        rows.append({
            "home": teams[0],
            "away": teams[1],
            "competition": m.get("name", ""),
            "time": date_str,
            "status": "live" if m.get("matchStarted") else "upcoming",
            "status_text": m.get("status", ""),
            "url": m.get("id", "")
        })

    if not rows:
        print("\n⚠️  No T20 matches found in API response.")
        df = pd.DataFrame(columns=[
            "home", "away", "competition", "time",
            "status", "status_text", "url"
        ])
        DATA_DIR.mkdir(exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)
        return

    df = pd.DataFrame(rows)

    # Parse dates
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)

    # Remove past matches (keep only future + live)
    now = pd.Timestamp.now(tz="UTC")
    df = df[df["time"] > now].copy()

    # Sort + dedupe
    df = df.sort_values("time").drop_duplicates(
        subset=["home", "away", "time"]
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ Upcoming T20 fixtures saved: {len(df)}")
    print(f"Saved file: {OUTPUT_FILE}")

    if len(df) > 0:
        print("\nUpcoming T20 Matches:")
        print(
            df[["home", "away", "competition", "time"]]
            .head(20)
            .to_string(index=False)
        )
    else:
        print("\n⚠️  No upcoming T20 matches at the moment.")


if __name__ == "__main__":
    fetch_fixtures()