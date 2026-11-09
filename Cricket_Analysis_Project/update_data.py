
import requests
import zipfile
from pathlib import Path

# Project folders
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ZIP_PATH = DATA_DIR / "icc_mens_t20_world_cup_json.zip"
EXTRACT_DIR = DATA_DIR / "icc_mens_t20_world_cup_male_json"

# Cricsheet download link
URL = "https://cricsheet.org/downloads/icc_mens_t20_world_cup_json.zip"

def update_cricket_data():

    DATA_DIR.mkdir(exist_ok=True)

    print("Downloading latest cricket data...")

    response = requests.get(URL, timeout=120)
    response.raise_for_status()

    ZIP_PATH.write_bytes(response.content)

    print("Download completed!")

    print("Extracting match files...")

    with zipfile.ZipFile(ZIP_PATH, "r") as zip_file:
        zip_file.extractall(EXTRACT_DIR)

    json_files = list(EXTRACT_DIR.rglob("*.json"))

    print(f"Total JSON match files: {len(json_files)}")
    print("Cricket data update completed successfully!")

if __name__ == "__main__":
    update_cricket_data()
