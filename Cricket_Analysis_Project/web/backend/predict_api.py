from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "models" / "cricket_winner_model.pkl"
DATA_PATH = BASE_DIR / "data" / "cleaned_cricket_matches.csv"

_model = None
_df = None


def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise HTTPException(500, f"Model not found at {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)
    return _model


def get_df():
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_PATH)
        _df["date"] = pd.to_datetime(_df["date"])
        _df["year"] = _df["date"].dt.year
    return _df


class PredictRequest(BaseModel):
    team1: str
    team2: str
    city: str
    venue: str
    toss_winner: str
    toss_decision: str
    year: int


@router.get("/options")
def get_options():
    df = get_df()
    teams = sorted(set(df["team1"].dropna()) | set(df["team2"].dropna()))
    cities = sorted(df["city"].dropna().unique())
    venues = sorted(df["venue"].dropna().unique())
    return {"teams": teams, "cities": cities, "venues": venues}


@router.post("/predict")
def predict(req: PredictRequest):
    if req.team1 == req.team2:
        raise HTTPException(400, "Team1 and Team2 must be different")

    model = get_model()

    input_data = pd.DataFrame([{
        "team1": req.team1,
        "team2": req.team2,
        "city": req.city,
        "venue": req.venue,
        "toss_winner": req.toss_winner,
        "toss_decision": req.toss_decision,
        "year": req.year
    }])

    try:
        prediction = model.predict(input_data)[0]
        probabilities = model.predict_proba(input_data)[0]
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")

    winner = req.team1 if prediction == 1 else req.team2

    return {
        "winner": winner,
        "team1": req.team1,
        "team2": req.team2,
        "team1_probability": round(float(probabilities[1]) * 100, 2),
        "team2_probability": round(float(probabilities[0]) * 100, 2)
    }
@router.get("/stats/{team}")
def get_team_stats(team: str):
    df = get_df()

    team_matches = df[
        (df["team1"] == team) | (df["team2"] == team)
    ].copy()

    total = len(team_matches)
    wins = int((team_matches["winner"] == team).sum())
    losses = total - wins
    win_pct = round((wins / total * 100), 2) if total > 0 else 0

    history_df = team_matches.sort_values("date", ascending=False).head(30)

    history = []
    for _, row in history_df.iterrows():
        history.append({
            "date": row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"]),
            "team1": row["team1"],
            "team2": row["team2"],
            "winner": row["winner"],
            "city": row.get("city", "")
        })

    return {
        "team": team,
        "played": total,
        "won": wins,
        "lost": losses,
        "win_percentage": win_pct,
        "history": history
    }