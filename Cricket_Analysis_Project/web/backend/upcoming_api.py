from fastapi import APIRouter
from pathlib import Path
import pandas as pd

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIXTURES_PATH = BASE_DIR / "data" / "mens_t20_upcoming.csv"
PREDICTIONS_PATH = BASE_DIR / "data" / "upcoming_predictions.csv"
LIVE_SCORES_PATH = BASE_DIR / "data" / "live_scores.csv"


def _read_csv_safe(path: Path):
    try:
        return pd.read_csv(path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()


@router.get("/upcoming")
def upcoming():
    fixtures = _read_csv_safe(FIXTURES_PATH)
    predictions = _read_csv_safe(PREDICTIONS_PATH)
    live_scores = _read_csv_safe(LIVE_SCORES_PATH)

    if fixtures.empty:
        return {"fixtures": [], "predictions": [], "live_scores": [],
                "metrics": {"total": 0, "predictions": 0, "waiting": 0}}

    if "time" in fixtures.columns:
        fixtures["time"] = pd.to_datetime(fixtures["time"], errors="coerce", utc=True)
        now = pd.Timestamp.now(tz="UTC")
        fixtures = fixtures[fixtures["time"] > now].copy()

    fixtures = fixtures.sort_values("time")

    def _make_key(t1, t2):
        a = " ".join(str(t1).strip().lower().split())
        b = " ".join(str(t2).strip().lower().split())
        return tuple(sorted([a, b]))

    pred_keys = set()
    if not predictions.empty:
        for _, r in predictions.iterrows():
            pred_keys.add(_make_key(r["team1"], r["team2"]))

    fixtures_list = []
    for _, r in fixtures.iterrows():
        t1 = r.get("home", "")
        t2 = r.get("away", "")
        fixtures_list.append({
            "team1": t1,
            "team2": t2,
            "competition": r.get("competition", ""),
            "time": str(r.get("time", "")),
            "has_prediction": _make_key(t1, t2) in pred_keys
        })

    live_list = []
    if not live_scores.empty:
        for _, r in live_scores.iterrows():
            live_list.append({
                "team1": r.get("home", ""),
                "team2": r.get("away", ""),
                "score_team1": r.get("score_team1", ""),
                "score_team2": r.get("score_team2", ""),
                "status": r.get("status", "")
            })

    predictions_list = []
    if not predictions.empty:
        for _, r in predictions.iterrows():
            predictions_list.append({
                "team1": r["team1"],
                "team2": r["team2"],
                "category": r.get("category", ""),
                "competition": r.get("competition", ""),
                "match_time": str(r.get("match_time", "")),
                "team1_recent_form": r.get("team1_recent_form", ""),
                "team1_recent_matches": int(r.get("team1_recent_matches", 0) or 0),
                "team1_international_matches": int(r.get("team1_international_matches", 0) or 0),
                "team1_total_history": int(r.get("team1_total_history", 0) or 0),
                "team1_estimated_share": float(r.get("team1_estimated_share", 0) or 0),
                "team2_recent_form": r.get("team2_recent_form", ""),
                "team2_recent_matches": int(r.get("team2_recent_matches", 0) or 0),
                "team2_international_matches": int(r.get("team2_international_matches", 0) or 0),
                "team2_total_history": int(r.get("team2_total_history", 0) or 0),
                "team2_estimated_share": float(r.get("team2_estimated_share", 0) or 0),
                "predicted_winner": r.get("predicted_winner", ""),
                "data_confidence": r.get("data_confidence", ""),
            })

    total = len(fixtures_list)
    total_pred = len(predictions_list)

    return {
        "fixtures": fixtures_list,
        "predictions": predictions_list,
        "live_scores": live_list,
        "metrics": {
            "total": total,
            "predictions": total_pred,
            "waiting": max(total - total_pred, 0)
        }
    }