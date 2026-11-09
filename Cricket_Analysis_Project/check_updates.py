
import pandas as pd
from pathlib import Path

data_dir = Path("data")

old_file = data_dir / "cleaned_cricket_matches.csv"
new_file = data_dir / "cleaned_cricket_matches.csv"

# The previous dataset was overwritten during rebuilding.
# So compare match IDs against the original ML dataset's dates
# and teams only as a basic reference.

old_ml_file = data_dir / "ml_dataset.csv"

old_df = pd.read_csv(old_ml_file)
new_df = pd.read_csv(new_file)

print("Previous ML dataset matches:", len(old_df))
print("Updated cleaned dataset matches:", len(new_df))

print("\nPrevious ML dataset columns:")
print(old_df.columns.tolist())

print("\nUpdated dataset columns:")
print(new_df.columns.tolist())

print("\nLatest match in updated dataset:")
print(new_df["date"].max())

print("\nDataset check completed.")
