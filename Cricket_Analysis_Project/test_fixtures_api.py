
import requests
from bs4 import BeautifulSoup

match_urls = [
    "https://sportscore.com/cricket/match/abu-dhabi-vs-ajman/",
    "https://sportscore.com/cricket/match/vancouver-guardians-vs-brampton-blazers/"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

for url in match_urls:
    print("\nChecking:", url)

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        print("Status Code:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")

        page_text = soup.get_text(" ", strip=True)

        print("\nPage Information:")
        print(page_text[:3000])

    except requests.RequestException as error:
        print("Error:", error)
