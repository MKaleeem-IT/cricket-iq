
import requests

url = "https://sportscore.com/api/v1/fixtures/"

# Test one older date
params = {
    "sport": "cricket",
    "date": "2025-10-29",
    "status": "finished",
    "limit": 100
}

try:
    response = requests.get(url, params=params, timeout=30)
    print("HTTP Status:", response.status_code)
    response.raise_for_status()

    data = response.json()
    matches = data.get("matches", [])

    print("Matches found:", len(matches))

    for match in matches:
        competition = match.get("competition", "")
        if "women" in str(competition).lower() or "interzonal" in str(competition).lower():
            print(
                match.get("home"),
                "vs",
                match.get("away"),
                "|",
                competition,
                "|",
                match.get("time")
            )

except requests.RequestException as error:
    print("API Error:", error)
