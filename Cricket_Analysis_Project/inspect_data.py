
import os
import json

# Dataset folder
data_folder = "data/icc_mens_t20_world_cup_male_json"

# Get all JSON files
files = [f for f in os.listdir(data_folder) if f.endswith(".json")]

print("Total Matches:", len(files))

# Read the first match
first_file = os.path.join(data_folder, files[0])

with open(first_file, "r", encoding="utf-8") as file:
    match_data = json.load(file)

# Display match information
print("\nFirst Match Data:")
print(json.dumps(match_data["info"], indent=4))

# Display innings information
print("\nNumber of Innings:", len(match_data["innings"]))

# Explore the first innings
first_innings = match_data["innings"][0]

print("\nBatting Team:", first_innings["team"])

# Explore the first over
first_over = first_innings["overs"][0]

print("\nOver Number:", first_over["over"])

# Display each delivery
for delivery in first_over["deliveries"]:
    print(delivery)
