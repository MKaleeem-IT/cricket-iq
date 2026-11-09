
import streamlit as st
import pandas as pd
import joblib

# STEP 1: PAGE CONFIGURATION
st.set_page_config(
    page_title="Cricket Match Predictor",
    page_icon="🏏",
    layout="centered"
)

# STEP 2: LOAD SAVED MODEL
model = joblib.load("models/cricket_winner_model.pkl")

# STEP 3: APP TITLE
st.title("🏏 Cricket Match Analysis")
st.subheader("Match Outcome Prediction Using Machine Learning")

st.write(
    "Enter match details below to predict the possible winner."
)

# STEP 4: LOAD AVAILABLE DATA FOR DROPDOWNS
df = pd.read_csv("data/cleaned_cricket_matches.csv")

teams = sorted(
    set(df["team1"].dropna()) |
    set(df["team2"].dropna())
)

cities = sorted(df["city"].dropna().unique())
venues = sorted(df["venue"].dropna().unique())

# STEP 5: USER INPUTS
st.header("Enter Match Details")

team1 = st.selectbox("Select Team 1", teams)

team2_options = [team for team in teams if team != team1]
team2 = st.selectbox("Select Team 2", team2_options)

city = st.selectbox("Select City", cities)

venue = st.selectbox("Select Venue", venues)

toss_winner = st.selectbox(
    "Select Toss Winner",
    [team1, team2]
)

toss_decision = st.selectbox(
    "Toss Decision",
    ["bat", "field"]
)

year = st.number_input(
    "Match Year",
    min_value=2014,
    max_value=2035,
    value=2026,
    step=1
)

# STEP 6: PREDICTION BUTTON
if st.button("Predict Match Winner"):

    # Prepare input data
    input_data = pd.DataFrame([{
        "team1": team1,
        "team2": team2,
        "city": city,
        "venue": venue,
        "toss_winner": toss_winner,
        "toss_decision": toss_decision,
        "year": year
    }])

    # Make prediction
    prediction = model.predict(input_data)[0]

    # Get prediction probability
    probabilities = model.predict_proba(input_data)[0]

    st.subheader("Prediction Result")

    if prediction == 1:
        st.success(f"Predicted Winner: {team1}")
    else:
        st.success(f"Predicted Winner: {team2}")

    st.write("Prediction Confidence (model probability):")

    st.write(
        f"Team 1 ({team1}): {probabilities[1] * 100:.2f}%"
    )

    st.write(
        f"Team 2 ({team2}): {probabilities[0] * 100:.2f}%"
    )

    st.info(
        "This is a machine learning prediction, not a guaranteed match result."
    )

# STEP 7: FOOTER
st.divider()

st.caption(
    "Cricket Match Analysis and Outcome Prediction Using Machine Learning"
)
