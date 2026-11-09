
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

# STEP 1: LOAD ML DATASET
df = pd.read_csv("data/ml_dataset.csv")

print("ML Dataset Loaded Successfully!")

# STEP 2: SELECT CATEGORICAL FEATURES
categorical_columns = [
    "team1",
    "team2",
    "city",
    "venue",
    "toss_winner",
    "toss_decision"
]

# STEP 3: APPLY ONE-HOT ENCODING
encoder = OneHotEncoder(
    handle_unknown="ignore",
    sparse_output=False
)

encoded_array = encoder.fit_transform(
    df[categorical_columns]
)

# STEP 4: CREATE ENCODED DATAFRAME
encoded_columns = encoder.get_feature_names_out(
    categorical_columns
)

encoded_df = pd.DataFrame(
    encoded_array,
    columns=encoded_columns
)

# STEP 5: KEEP NUMERICAL FEATURE
encoded_df["year"] = df["year"]

# STEP 6: ADD TARGET COLUMN
encoded_df["team1_won"] = df["team1_won"]

# STEP 7: CHECK ENCODED DATASET
print("\nEncoded Dataset:")
print(encoded_df.head())

print("\nEncoded Dataset Shape:")
print(encoded_df.shape)

print("\nMissing Values:")
print(encoded_df.isnull().sum().sum())

# STEP 8: SAVE ENCODED DATASET
encoded_df.to_csv(
    "data/encoded_cricket_dataset.csv",
    index=False
)

print("\nEncoded Dataset Saved Successfully!")
