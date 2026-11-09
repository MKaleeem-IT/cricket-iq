import pandas as pd

# =========================================================
# FILE PATHS
# =========================================================

UPCOMING_FILE = "data/mens_t20_upcoming.csv"
RESULTS_FILE = "mens_t20_data/prepared_recent_results.csv"

MEN_INTL_FILE = "data/mens_international_t20.csv"
WOMEN_INTL_FILE = "data/womens_international_t20.csv"

OUTPUT_FILE = "data/upcoming_predictions.csv"

# Minimum combined recent + international history
MIN_MATCHES_FOR_PREDICTION = 2

RECENT_MATCH_LIMIT = 5
INTERNATIONAL_MATCH_LIMIT = 10

# Recent form remains the main factor
RECENT_WEIGHT = 0.70
INTERNATIONAL_WEIGHT = 0.30

# Expected columns for empty CSV safety
EXPECTED_COLUMNS = [
    "team1", "team2", "category", "competition", "match_time",
    "team1_recent_form", "team1_recent_matches", "team1_wins",
    "team1_draws", "team1_losses",
    "team1_international_form", "team1_international_matches",
    "team1_international_wins", "team1_total_history",
    "team1_estimated_share",
    "team2_recent_form", "team2_recent_matches", "team2_wins",
    "team2_draws", "team2_losses",
    "team2_international_form", "team2_international_matches",
    "team2_international_wins", "team2_total_history",
    "team2_estimated_share",
    "predicted_winner", "data_confidence", "prediction_status",
]


# =========================================================
# LOAD DATASETS
# =========================================================

upcoming = pd.read_csv(UPCOMING_FILE)
results = pd.read_csv(RESULTS_FILE)

mens_intl = pd.read_csv(MEN_INTL_FILE)
womens_intl = pd.read_csv(WOMEN_INTL_FILE)

print("Upcoming fixtures loaded:", len(upcoming))
print("Recent results loaded:", len(results))
print("Men's international matches loaded:", len(mens_intl))
print("Women's international matches loaded:", len(womens_intl))


# =========================================================
# VALIDATE REQUIRED COLUMNS
# =========================================================

upcoming_required = [
    "home", "away", "time", "competition"
]

results_required = [
    "home", "away", "time", "winner",
    "competition", "match_category", "result",
    "winner_source"
]

international_required = [
    "team1", "team2", "date", "winner",
    "result", "category"
]


def validate_columns(df, required, filename):

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in {filename}: {missing}"
        )


validate_columns(
    upcoming, upcoming_required, UPCOMING_FILE
)

validate_columns(
    results, results_required, RESULTS_FILE
)

validate_columns(
    mens_intl, international_required, MEN_INTL_FILE
)

validate_columns(
    womens_intl, international_required, WOMEN_INTL_FILE
)


# =========================================================
# CLEAN TEXT AND DATES  (FIXED: remove " Women" suffix)
# =========================================================

def clean_name(name):
    if pd.isna(name):
        return ""
    name = str(name).strip()
    # Remove " Women" / " women" suffix so women's teams match base names
    name = name.replace(" Women", "").replace(" women", "").strip()
    return " ".join(name.lower().split())


upcoming["time"] = pd.to_datetime(
    upcoming["time"],
    errors="coerce",
    utc=True
)

results["time"] = pd.to_datetime(
    results["time"],
    errors="coerce",
    utc=True
)

mens_intl["date"] = pd.to_datetime(
    mens_intl["date"],
    errors="coerce",
    utc=True
)

womens_intl["date"] = pd.to_datetime(
    womens_intl["date"],
    errors="coerce",
    utc=True
)


# Clean recent results

for col in [
    "home", "away", "winner",
    "match_category", "result", "winner_source"
]:
    results[col] = (
        results[col]
        .astype("string")
        .str.strip()
    )


# Clean international results

for df in [mens_intl, womens_intl]:

    for col in [
        "team1", "team2", "winner",
        "category", "result"
    ]:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )


# =========================================================
# REMOVE INCOMPLETE AND UNVERIFIED RECENT RESULTS
# =========================================================

results = results.dropna(
    subset=[
        "time", "winner", "home",
        "away", "match_category", "result"
    ]
).copy()


# Remove empty team names

results = results[
    (results["home"] != "") &
    (results["away"] != "") &
    (results["winner"] != "")
].copy()


# Exclude unverified score-inferred winners
# (kept for safety, but we no longer block these rows from prediction;
#  they still count towards form if winner is known)

results["winner_source_clean"] = (
    results["winner_source"]
    .apply(clean_name)
)

# NOTE: We keep score_inferred rows because they still contain a valid winner.
# Only drop rows with missing winner / result.

results = results[
    (results["winner_source_clean"] != "")
].copy()


print(
    "Verified recent results retained:",
    len(results)
)


# =========================================================
# CATEGORY DETECTION
# =========================================================

def get_category(match):

    competition = str(
        match.get("competition", "")
    ).lower()

    home = str(
        match.get("home", "")
    ).lower()

    away = str(
        match.get("away", "")
    ).lower()

    combined = f"{competition} {home} {away}"

    if "women" in combined or "woman" in combined:
        return "Women's T20"

    return "Men's T20"


# =========================================================
# INTERNATIONAL DATA PREPARATION
# =========================================================

international = pd.concat(
    [mens_intl, womens_intl],
    ignore_index=True
)


international = international.dropna(
    subset=[
        "date", "team1", "team2",
        "winner", "category", "result"
    ]
).copy()


# Remove No Result matches from win/loss calculations

international = international[
    international["winner"].apply(clean_name).ne("no result") &
    international["result"].apply(clean_name).ne("no result")
].copy()


# =========================================================
# MATCH FORM CALCULATION
# =========================================================

def calculate_rating(wins, draws, total):

    if total == 0:
        return 0.5

    points = wins + (0.5 * draws)

    win_rate = (points + 1) / (total + 2)

    reliability = total / (total + 5)

    return 0.5 + (
        (win_rate - 0.5) * reliability
    )


def calculate_team_record(
    team,
    match_time,
    category,
    dataset,
    source_type,
    limit
):

    team_key = clean_name(team)

    empty_record = {
        "matches": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "form": "No data",
        "rating": 0.5
    }

    if not team_key:
        return empty_record


    # -----------------------------------------------------
    # RECENT RESULTS
    # -----------------------------------------------------

    if source_type == "recent":

        category_data = dataset[
            dataset["match_category"] == category
        ]

        previous = category_data[
            category_data["time"] < match_time
        ]

        team_matches = previous[
            (
                previous["home"].apply(clean_name)
                == team_key
            ) |
            (
                previous["away"].apply(clean_name)
                == team_key
            )
        ].sort_values("time").tail(limit)


    # -----------------------------------------------------
    # INTERNATIONAL RESULTS
    # -----------------------------------------------------

    else:

        category_data = dataset[
            dataset["category"] == category
        ]

        previous = category_data[
            category_data["date"] < match_time
        ]

        team_matches = previous[
            (
                previous["team1"].apply(clean_name)
                == team_key
            ) |
            (
                previous["team2"].apply(clean_name)
                == team_key
            )
        ].sort_values("date").tail(limit)


    wins = 0
    draws = 0
    losses = 0

    form = []


    # -----------------------------------------------------
    # CALCULATE WINS, DRAWS AND LOSSES
    # -----------------------------------------------------

    for _, historical_match in team_matches.iterrows():

        result = clean_name(
            historical_match["result"]
        )

        winner = clean_name(
            historical_match["winner"]
        )

        if result in ["match drawn", "draw", "tie", "no result"]:

            draws += 1
            form.append("D")

        elif winner == team_key:

            wins += 1
            form.append("W")

        else:

            losses += 1
            form.append("L")


    total = len(team_matches)

    rating = calculate_rating(
        wins, draws, total
    )


    return {
        "matches": total,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "form": " ".join(form) if form else "No data",
        "rating": rating
    }


# =========================================================
# COMBINED TEAM RATING
# =========================================================

def get_team_form(team, match_time, category):

    recent = calculate_team_record(
        team,
        match_time,
        category,
        results,
        "recent",
        RECENT_MATCH_LIMIT
    )


    international_form = calculate_team_record(
        team,
        match_time,
        category,
        international,
        "international",
        INTERNATIONAL_MATCH_LIMIT
    )


    recent_count = recent["matches"]

    international_count = (
        international_form["matches"]
    )


    # -----------------------------------------------------
    # COMBINE RECENT AND INTERNATIONAL RATINGS
    # -----------------------------------------------------

    if recent_count > 0 and international_count > 0:

        rating = (
            RECENT_WEIGHT * recent["rating"]
            + INTERNATIONAL_WEIGHT
            * international_form["rating"]
        )

    elif recent_count > 0:

        rating = recent["rating"]

    elif international_count > 0:

        rating = international_form["rating"]

    else:

        rating = 0.5


    total_history = (
        recent_count + international_count
    )


    return {

        "matches": recent_count,

        "wins": recent["wins"],

        "draws": recent["draws"],

        "losses": recent["losses"],

        "form": recent["form"],


        "international_matches": international_count,

        "international_wins": (
            international_form["wins"]
        ),

        "international_draws": (
            international_form["draws"]
        ),

        "international_losses": (
            international_form["losses"]
        ),

        "international_form": (
            international_form["form"]
        ),


        "total_history": total_history,

        "rating": rating
    }


# =========================================================
# GENERATE UPCOMING PREDICTIONS
# =========================================================

predictions = []


# Current UTC time for removing past fixtures

current_time = pd.Timestamp.now(tz="UTC")


for _, match in upcoming.iterrows():

    team1 = match["home"]

    team2 = match["away"]

    match_time = match["time"]


    # -----------------------------------------------------
    # SKIP INVALID FIXTURES
    # -----------------------------------------------------

    if pd.isna(match_time):
        continue

    if pd.isna(team1) or pd.isna(team2):
        continue

    if clean_name(team1) == "" or clean_name(team2) == "":
        continue


    # -----------------------------------------------------
    # REMOVE PAST FIXTURES
    # -----------------------------------------------------

    if match_time <= current_time:
        continue


    category = get_category(match)


    # -----------------------------------------------------
    # GET TEAM FORM
    # -----------------------------------------------------

    form1 = get_team_form(
        team1, match_time, category
    )

    form2 = get_team_form(
        team2, match_time, category
    )


    # -----------------------------------------------------
    # MINIMUM HISTORY CHECK
    # -----------------------------------------------------

    minimum_history = min(
        form1["total_history"],
        form2["total_history"]
    )


    # Hide match if either team has fewer than 2 matches

    if minimum_history < MIN_MATCHES_FOR_PREDICTION:
        continue


    # -----------------------------------------------------
    # CALCULATE INDICATIVE SHARES
    # -----------------------------------------------------

    total_rating = (
        form1["rating"] + form2["rating"]
    )


    if total_rating > 0:

        estimate1 = (
            form1["rating"] / total_rating
        ) * 100

        estimate2 = (
            form2["rating"] / total_rating
        ) * 100

    else:

        estimate1 = 50

        estimate2 = 50


    # -----------------------------------------------------
    # DATA CONFIDENCE
    # -----------------------------------------------------

    minimum_recent = min(
        form1["matches"],
        form2["matches"]
    )


    if minimum_recent < 3:

        confidence = "Limited recent data"

    elif minimum_history < 10:

        confidence = "Moderate data coverage"

    else:

        confidence = "Better data coverage"


    # -----------------------------------------------------
    # PREDICT WINNER
    # -----------------------------------------------------

    winner = (
        team1
        if form1["rating"] >= form2["rating"]
        else team2
    )


    prediction_status = "Combined-form estimate"


    # -----------------------------------------------------
    # SAVE ELIGIBLE MATCH
    # -----------------------------------------------------

    predictions.append({

        "team1": team1,

        "team2": team2,

        "category": category,

        "competition": match["competition"],

        "match_time": match_time,


        "team1_recent_form": form1["form"],

        "team1_recent_matches": form1["matches"],

        "team1_wins": form1["wins"],

        "team1_draws": form1["draws"],

        "team1_losses": form1["losses"],


        "team1_international_form": (
            form1["international_form"]
        ),

        "team1_international_matches": (
            form1["international_matches"]
        ),

        "team1_international_wins": (
            form1["international_wins"]
        ),


        "team1_total_history": (
            form1["total_history"]
        ),

        "team1_estimated_share": round(
            estimate1, 2
        ),


        "team2_recent_form": form2["form"],

        "team2_recent_matches": form2["matches"],

        "team2_wins": form2["wins"],

        "team2_draws": form2["draws"],

        "team2_losses": form2["losses"],


        "team2_international_form": (
            form2["international_form"]
        ),

        "team2_international_matches": (
            form2["international_matches"]
        ),

        "team2_international_wins": (
            form2["international_wins"]
        ),


        "team2_total_history": (
            form2["total_history"]
        ),

        "team2_estimated_share": round(
            estimate2, 2
        ),


        "predicted_winner": winner,

        "data_confidence": confidence,

        "prediction_status": prediction_status
    })


# =========================================================
# SAVE PREDICTIONS
# =========================================================

prediction_df = pd.DataFrame(predictions)


# Empty case: still write header so read_csv never fails
if prediction_df.empty:
    prediction_df = pd.DataFrame(columns=EXPECTED_COLUMNS)


prediction_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print("\nUPCOMING T20 COMBINED-FORM ESTIMATES")

print("=" * 75)


if prediction_df.empty:

    print(
        "Other: No upcoming matches have sufficient "
        "historical data for prediction."
    )


else:

    for _, row in prediction_df.iterrows():

        print(
            f"\nCategory: {row['category']}"
        )

        print(
            f"Match: {row['team1']} vs {row['team2']}"
        )

        print(
            f"Competition: {row['competition']}"
        )

        print(
            f"Date: {row['match_time']}"
        )


        # TEAM 1

        print("\nTEAM 1:", row["team1"])

        print(
            "Recent form:",
            row["team1_recent_form"]
        )

        print(
            "Recent matches:",
            row["team1_recent_matches"]
        )

        print(
            "International form:",
            row["team1_international_form"]
        )

        print(
            "International matches:",
            row["team1_international_matches"]
        )

        print(
            "Total history:",
            row["team1_total_history"]
        )

        print(
            "Indicative share:",
            str(
                row["team1_estimated_share"]
            ) + "%"
        )


        # TEAM 2

        print("\nTEAM 2:", row["team2"])

        print(
            "Recent form:",
            row["team2_recent_form"]
        )

        print(
            "Recent matches:",
            row["team2_recent_matches"]
        )

        print(
            "International form:",
            row["team2_international_form"]
        )

        print(
            "International matches:",
            row["team2_international_matches"]
        )

        print(
            "Total history:",
            row["team2_total_history"]
        )

        print(
            "Indicative share:",
            str(
                row["team2_estimated_share"]
            ) + "%"
        )


        # PREDICTION

        print(
            "\nEstimated winner:",
            row["predicted_winner"]
        )

        print(
            "Prediction status:",
            row["prediction_status"]
        )

        print(
            "Data coverage:",
            row["data_confidence"]
        )

        print("-" * 75)


# =========================================================
# CATEGORY SUMMARY
# =========================================================

print("\nCATEGORY SUMMARY")


if not prediction_df.empty:

    print(
        prediction_df["category"]
        .value_counts()
        .to_string()
    )


    print("\nPREDICTION STATUS SUMMARY")

    print(
        prediction_df["prediction_status"]
        .value_counts()
        .to_string()
    )


# =========================================================
# FINAL OUTPUT
# =========================================================

print(
    "\nEligible predictions saved to:",
    OUTPUT_FILE
)