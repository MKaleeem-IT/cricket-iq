
import requests
from datetime import datetime, timezone

url = "https://sportscore.com/api/v1/fixtures/"

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

params = {
    "sport": "cricket",
    "date": today,
    "status": "finished",
    "limit": 100
}

response = requests.get(url, params=params, timeout=30)

print("Status Code:", response.status_code)

data = response.json()
matches = data.get("matches", [])

print("\nCompleted Matches Found:", len(matches))

for match in matches:
    print("\nMatch:", match.get("home"), "vs", match.get("away"))
    print("Competition:", match.get("competition"))
    print("Home Score:", match.get("home_score"))
    print("Away Score:", match.get("away_score"))
    print("Status:", match.get("status"))
