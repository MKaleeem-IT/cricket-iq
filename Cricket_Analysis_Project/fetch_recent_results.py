
import requests
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

API_URL = "https://sportscore.com/api/v1/fixtures/"
OUTPUT_FILE = "mens_t20_data/recent_completed_matches.csv"

# Collect one year of historical matches
LOOKBACK_DAYS = 365

all_matches = []

today = datetime.now(timezone.utc).date()

print("Fetching completed cricket matches...")
print(f"Collection period: Previous {LOOKBACK_DAYS} days")
print("=" * 60)

session = requests.Session()

for day in range(1, LOOKBACK_DAYS + 1):
    match_date = today - timedelta(days=day)

    params = {
        "sport": "cricket",
        "date": match_date.strftime("%Y-%m-%d"),
        "status": "finished",
        "limit": 100
    }

    try:
        response = session.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            print(f"{match_date}: Unexpected API response format")
            continue

        matches = data.get("matches", [])

        if not isinstance(matches, list):
            print(f"{match_date}: Invalid matches field")
            continue

        all_matches.extend(matches)

        if matches:
            print(f"{match_date}: {len(matches)} completed matches")

    except requests.exceptions.Timeout:
        print(f"{match_date}: Request timed out")

    except requests.exceptions.HTTPError as error:
        print(f"{match_date}: HTTP error - {error}")

    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"{match_date}: Request/API error - {error}")

    time.sleep(0.2)

session.close()

# Convert API records into a DataFrame
df = pd.DataFrame(all_matches)

if not df.empty:

    # Remove duplicate fixtures
    if "url" in df.columns:
        df = df.drop_duplicates(subset=["url"])
    else:
        df = df.drop_duplicates()

    # Ensure output directory exists
    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

    # Save all available API fields
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n" + "=" * 60)
    print("DATA COLLECTION SUMMARY")
    print("=" * 60)

    print("Total unique completed matches:", len(df))

    if "competition" in df.columns:
        print("\nTop 20 Competitions:")
        print(df["competition"].value_counts().head(20).to_string())

    print("\nAvailable API columns:")
    print(df.columns.tolist())

    print("\nSample records:")
    print(df.head(5).to_string(index=False))

    print(f"\nSaved successfully: {OUTPUT_FILE}")

else:
    print("\nNo completed matches found.")
    print("The previous output file has not been overwritten.")
