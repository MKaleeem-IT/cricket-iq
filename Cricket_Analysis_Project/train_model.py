
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# STEP 1: LOAD CLEANED DATASET
df = pd.read_csv("data/cleaned_cricket_matches.csv")

df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

# STEP 2: CREATE TARGET
df["team1_won"] = (
    df["winner"] == df["team1"]
).astype(int)

# STEP 3: SORT BY EXACT MATCH DATE
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

# STEP 5: CHRONOLOGICAL SPLIT
split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("Training Matches:", len(X_train))
print("Testing Matches:", len(X_test))

print("\nTraining Date Range:")
print(df.iloc[:split_index]["date"].min(),
      "to",
      df.iloc[:split_index]["date"].max())

print("\nTesting Date Range:")
print(df.iloc[split_index:]["date"].min(),
      "to",
      df.iloc[split_index:]["date"].max())

# STEP 6: ENCODING
categorical_features = [
    "team1",
    "team2",
    "city",
    "venue",
    "toss_winner",
    "toss_decision"
]

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

# STEP 7: CREATE PIPELINE
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000))
    ]
)

# STEP 8: TRAIN MODEL
model.fit(X_train, y_train)

print("\nModel Training Completed!")

# STEP 9: PREDICTION
y_pred = model.predict(X_test)

# STEP 10: EVALUATION
print("\nModel Accuracy:",
      round(accuracy_score(y_test, y_pred) * 100, 2), "%")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))
