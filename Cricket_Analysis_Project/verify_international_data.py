
import pandas as pd

files = [
    "data/mens_international_t20.csv",
    "data/womens_international_t20.csv"
]

for file in files:
    df = pd.read_csv(file)

    print("\n" + "=" * 50)
    print("FILE:", file)
    print("=" * 50)

    print("Rows:", len(df))
    print("Unique matches:", df["match_id"].nunique())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nWinner counts:")
    print(df["winner"].value_counts(dropna=False).head(10))

    print("\nSample matches:")
    print(
        df[[
            "date", "team1", "team2",
            "winner", "team1_score", "team2_score"
        ]].head(5).to_string(index=False)
    )
