
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

# STEP 1: LOAD DATA
df = pd.read_csv("data/cleaned_cricket_matches.csv")

df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

# STEP 2: CREATE TARGET
df["team1_won"] = (
    df["winner"] == df["team1"]
).astype(int)

# STEP 3: SORT DATA BY DATE
df = df.sort_values("date").reset_index(drop=True)

# STEP 4: SELECT FEATURES
features = [
    "team1",
    "team2",
    "city",
    "venue",
    "toss_winner",
    "toss_decision",
    "year"
]

X = df[features]
y = df["team1_won"]

# STEP 5: SELECT CATEGORICAL FEATURES
categorical_features = [
    "team1",
    "team2",
    "city",
    "venue",
    "toss_winner",
    "toss_decision"
]

# STEP 6: CREATE PREPROCESSOR
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ],
    remainder="passthrough"
)

# STEP 7: CREATE LOGISTIC REGRESSION PIPELINE
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            LogisticRegression(max_iter=1000)
        )
    ]
)

# STEP 8: TRAIN FINAL MODEL ON ALL AVAILABLE DATA
model.fit(X, y)

# STEP 9: SAVE MODEL
joblib.dump(
    model,
    "models/cricket_winner_model.pkl"
)

print("Final Logistic Regression Model Saved Successfully!")
