import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import subprocess
import sys
from pathlib import Path

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Cricket IQ | Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. CUSTOM DARK SPORTS THEME
# =====================================================

st.markdown("""

<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0B1120;
    color: #F1F5F9;
}

[data-testid="stHeader"] {
    background-color: #0B1120;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111B2E 0%, #0D1728 100%);
    border-right: 1px solid #26344D;
}

section[data-testid="stSidebar"] p {
    color: #CBD5E1;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    color: #4ADE80 !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: #17243A;
    border: 1px solid #293B57;
    border-radius: 12px;
    padding: 12px 14px;
    margin: 4px 0;
    min-height: 48px;
    transition: background 0.2s ease, border-color 0.2s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #CBD5E1 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #243B5A;
    border-color: #38BDF8;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, #164E38, #17365D);
    border: 1px solid #22C55E;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #4ADE80 !important;
    font-weight: 800 !important;
}

h1, h2, h3 {
    color: #F8FAFC !important;
    font-weight: 800 !important;
}

p, label {
    color: #CBD5E1;
}

.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 5px;
}

.subtitle {
    color: #94A3B8;
    font-size: 14px;
    margin-bottom: 25px;
}

.section-title {
    color: #F8FAFC;
    font-size: 20px;
    font-weight: 700;
    margin-top: 22px;
    margin-bottom: 15px;
}

.metric-card {
    background: linear-gradient(145deg, #17243A, #111B2E);
    border: 1px solid #293B57;
    border-radius: 14px;
    padding: 20px;
    min-height: 115px;
}

.metric-label {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

.metric-value {
    color: #F8FAFC;
    font-size: 27px;
    font-weight: 800;
    margin-top: 10px;
}

.metric-accent {
    color: #4ADE80;
}

.info-card {
    background-color: #17243A;
    border: 1px solid #293B57;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 15px;
}

.prediction-card {
    background: linear-gradient(135deg, #17243A, #1D3049);
    border: 1px solid #3A5273;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    margin-top: 20px;
}

.winner-text {
    color: #4ADE80;
    font-size: 30px;
    font-weight: 800;
}

.stButton > button {
    background: linear-gradient(90deg, #16A34A, #22C55E);
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 22px;
    font-weight: 700;
    width: 100%;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #15803D;
    color: white;
    border: none;
}

div[data-baseweb="select"] > div {
    background-color: #17243A;
    border-color: #344762;
    color: white;
}

div[data-baseweb="input"] > div {
    background-color: #17243A;
    border-color: #344762;
}

.stTabs [data-baseweb="tab"] {
    color: #CBD5E1;
}

hr {
    border-color: #293B57;
}

.footer {
    text-align: center;
    color: #64748B;
    font-size: 12px;
    padding: 25px 0 10px 0;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. LOAD MODEL AND DATA
# =====================================================

@st.cache_resource
def load_model():
    return joblib.load("models/cricket_winner_model.pkl")


@st.cache_data
def load_data():
    data = pd.read_csv("data/cleaned_cricket_matches.csv")
    data["date"] = pd.to_datetime(data["date"])
    data["year"] = data["date"].dt.year
    return data


# Load upcoming predictions safely (handles empty CSV)
@st.cache_data
def load_upcoming_predictions():
    path = "data/upcoming_predictions.csv"
    try:
        return pd.read_csv(path)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame()


# Load all upcoming fixtures safely
@st.cache_data
def load_upcoming_fixtures():
    path = "data/mens_t20_upcoming.csv"
    try:
        df = pd.read_csv(path)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame()
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    return df
@st.cache_data(ttl=60)  # 60 second baad refresh hoga
def load_live_scores():
    path = "data/live_scores.csv"
    try:
        return pd.read_csv(path)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame()

def run_upcoming_pipeline():
    scripts = [
        "fetch_upcoming.py",
        "filter_upcoming.py",
        "fetch_recent_results.py",
        "filter_recent_results.py",
        "prepare_recent_results.py",
        "upcoming_prediction.py",
        "fetch_live_scores.py"   # 👈 NAYA
    ]

    project_folder = Path(__file__).resolve().parent

    for script in scripts:
        result = subprocess.run(
            [sys.executable, str(project_folder / script)],
            capture_output=True,
            text=True,
            cwd=project_folder,
            timeout=600
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"{script} failed:\n{result.stdout}\n{result.stderr}"
            )


model = load_model()
df = load_data()

teams = sorted(
    set(df["team1"].dropna()) |
    set(df["team2"].dropna())
)

cities = sorted(df["city"].dropna().unique())
venues = sorted(df["venue"].dropna().unique())


# =====================================================
# 4. SIDEBAR NAVIGATION
# =====================================================

st.sidebar.markdown("""
<div style="text-align:center; padding:15px 0 25px 0;">
    <div style="font-size:42px;">🏏</div>
    <div style="font-size:24px; font-weight:800; color:#4ADE80;">
        CRICKET IQ
    </div>
    <div style="font-size:11px; color:#94A3B8; letter-spacing:2px;">
        SPORTS ANALYTICS
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "🏠 Dashboard",
        "🏆 Match Prediction",
        "🔮 Upcoming Match Prediction",
        "📊 Team Statistics",
        "ℹ️ About Project"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
<div style="background:#17243A; padding:15px; border-radius:12px;">
    <div style="color:#4ADE80; font-weight:700;">
        MODEL STATUS
    </div>
    <div style="color:#CBD5E1; font-size:13px; margin-top:7px;">
        ● Logistic Regression Active
    </div>
    <div style="color:#94A3B8; font-size:12px;">
        Test Accuracy: 67.39%
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="footer">
    Cricket IQ<br>
    Machine Learning Project
</div>
""", unsafe_allow_html=True)


# =====================================================
# 5. DASHBOARD PAGE
# =====================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">🏏 Cricket Analytics Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Explore cricket performance, historical data and machine learning insights.</div>',
        unsafe_allow_html=True
    )

    total_matches = len(df)
    total_teams = len(teams)

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("TOTAL MATCHES", total_matches, ""),
        ("TOTAL TEAMS", total_teams, ""),
        ("MODEL ACCURACY", "67.39%", "metric-accent"),
        ("ML ALGORITHM", "Logistic Regression", "")
    ]

    for col, (label, value, accent) in zip(
        [col1, col2, col3, col4], metrics
    ):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value {accent}">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">📈 Cricket Performance Overview</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.markdown(
            '<div class="info-card"><b>Top 10 Winning Teams</b></div>',
            unsafe_allow_html=True
        )

        wins = df["winner"].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor("#17243A")
        ax.set_facecolor("#17243A")

        wins.sort_values().plot(
            kind="barh",
            ax=ax,
            color="#22C55E"
        )

        ax.set_xlabel("Matches Won", color="white")
        ax.tick_params(colors="white")
        ax.set_ylabel("")
        ax.grid(axis="x", alpha=0.15)

        for spine in ax.spines.values():
            spine.set_color("#344762")

        st.pyplot(fig)
        plt.close(fig)

    with chart_col2:

        st.markdown(
            '<div class="info-card"><b>Matches Played Per Year</b></div>',
            unsafe_allow_html=True
        )

        yearly = df.groupby("year").size()

        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor("#17243A")
        ax.set_facecolor("#17243A")

        yearly.plot(
            kind="bar",
            ax=ax,
            color="#38BDF8"
        )

        ax.set_xlabel("Year", color="white")
        ax.set_ylabel("Matches", color="white")
        ax.tick_params(colors="white")
        ax.grid(axis="y", alpha=0.15)

        for spine in ax.spines.values():
            spine.set_color("#344762")

        st.pyplot(fig)
        plt.close(fig)

    st.markdown(
        '<div class="section-title">💡 About This Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
        <h3>Cricket Match Analysis & Prediction</h3>
        <p>
        This project uses historical ICC Men's T20 World Cup match data
        to analyze team performance and predict possible match winners.
        </p>
        <p>
        The system combines data analysis, visualization and
        Logistic Regression to provide match predictions after the toss.
        </p>
    </div>
    """, unsafe_allow_html=True)
    # =====================================================
# 6. HISTORICAL MATCH PREDICTION PAGE
# =====================================================

elif page == "🏆 Match Prediction":

    st.markdown(
        '<div class="main-title">🏆 Match Winner Prediction</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Enter match details and generate a machine learning prediction.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">⚔️ Select Your Teams</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox("TEAM 1", teams)

    with col2:
        team2_options = [
            team for team in teams if team != team1
        ]

        team2 = st.selectbox("TEAM 2", team2_options)

    st.markdown("---")

    st.markdown(
        '<div class="section-title">📍 Match Information</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        city = st.selectbox("MATCH CITY", cities)
        venue = st.selectbox("MATCH VENUE", venues)

    with col2:
        toss_winner = st.selectbox(
            "TOSS WINNER",
            [team1, team2]
        )

        toss_decision = st.selectbox(
            "TOSS DECISION",
            ["bat", "field"]
        )

    year = st.number_input(
        "MATCH YEAR",
        min_value=2014,
        max_value=2035,
        value=2026,
        step=1
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡ PREDICT MATCH WINNER"):

        input_data = pd.DataFrame([{
            "team1": team1,
            "team2": team2,
            "city": city,
            "venue": venue,
            "toss_winner": toss_winner,
            "toss_decision": toss_decision,
            "year": year
        }])

        prediction = model.predict(input_data)[0]
        probabilities = model.predict_proba(input_data)[0]

        winner = team1 if prediction == 1 else team2

        team1_probability = probabilities[1] * 100
        team2_probability = probabilities[0] * 100

        st.markdown(f"""
        <div class="prediction-card">
            <div style="color:#94A3B8; font-size:13px; font-weight:700;">
                MACHINE LEARNING PREDICTION
            </div>
            <div style="font-size:45px; margin:12px 0;">🏆</div>
            <div class="winner-text">{winner}</div>
            <div style="color:#CBD5E1; margin-top:8px;">
                Predicted Match Winner
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">📊 Prediction Probabilities</div>',
            unsafe_allow_html=True
        )

        pcol1, pcol2 = st.columns(2)

        pcol1.metric(
            team1,
            f"{team1_probability:.2f}%"
        )

        pcol2.metric(
            team2,
            f"{team2_probability:.2f}%"
        )

        st.progress(
            float(team1_probability / 100),
            text=f"{team1} predicted probability"
        )

        st.info(
            "These probabilities are model estimates, not guaranteed "
            "real-world winning chances."
        )


# =====================================================
# 7. UPCOMING MATCH PREDICTION PAGE
# =====================================================

elif page == "🔮 Upcoming Match Prediction":

    st.markdown(
        '<div class="main-title">🔮 Upcoming Match Predictions</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Today's upcoming fixtures and "
        "predictions where enough team history is available.</div>",
        unsafe_allow_html=True
    )

    # ---------- Manual refresh ----------
    if st.button("🔄 Refresh All Data & Predictions"):
        try:
            with st.spinner("Updating fixtures, recent results and predictions..."):
                run_upcoming_pipeline()
            load_upcoming_predictions.clear()
            load_upcoming_fixtures.clear()
            st.success("Data and predictions updated successfully!")
            st.rerun()
        except Exception as error:
            st.error(f"Update failed: {error}")

    st.markdown("---")

    # ---------- Load both files (loaders are already safe) ----------
    fixtures_df = load_upcoming_fixtures()
    predictions_df = load_upcoming_predictions()

    if fixtures_df.empty and predictions_df.empty:
        st.warning("No upcoming T20 matches are currently available.")
        st.stop()

    def _to_int(v):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return 0

    # ---------- Filter to FUTURE fixtures only ----------
    now_utc = pd.Timestamp.now(tz="UTC")

    if not fixtures_df.empty and "time" in fixtures_df.columns:
        fixtures_df = fixtures_df[
            pd.to_datetime(fixtures_df["time"], errors="coerce", utc=True) > now_utc
        ].copy()

    # ---------- Match keys to know which fixtures are predictable ----------
    def _make_key(team1, team2):
        t1 = " ".join(str(team1).strip().lower().split())
        t2 = " ".join(str(team2).strip().lower().split())
        return tuple(sorted([t1, t2]))

    prediction_keys = set()
    if not predictions_df.empty:
        for _, r in predictions_df.iterrows():
            prediction_keys.add(_make_key(r["team1"], r["team2"]))

    # ---------- Top metrics ----------
    total_fixtures = len(fixtures_df) if not fixtures_df.empty else len(predictions_df)
    total_predictions = len(predictions_df)
    waiting_for_data = max(total_fixtures - total_predictions, 0)

    c1, c2, c3 = st.columns(3)
    c1.metric("UPCOMING MATCHES", total_fixtures)
    c2.metric("PREDICTIONS AVAILABLE", total_predictions)
    c3.metric("WAITING FOR DATA", waiting_for_data)

    st.markdown("---")

           # =================================================
    # SECTION 1 — ALL UPCOMING MATCHES (future only)
    # =================================================
    st.markdown(
        '<div class="section-title">📅 All Upcoming Matches</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"Showing **{total_fixtures}** future matches. "
        f"Out of these, **{total_predictions}** have predictions available — "
        f"**{waiting_for_data}** are waiting for team data."
    )

    # 👇 Live scores load karo
    live_scores_df = load_live_scores()

    if fixtures_df.empty:
        st.info(
            "No upcoming fixtures available right now. "
            "Please refresh the data."
        )
    else:
        for _, match in fixtures_df.sort_values("time").iterrows():
            team1 = match.get("home", "")
            team2 = match.get("away", "")
            competition = match.get("competition", "")
            kickoff = match.get("time", "")

            # Check prediction availability
            has_prediction = _make_key(team1, team2) in prediction_keys

            if has_prediction:
                st.markdown(
                    f"**🏏 {team1} vs {team2}** &nbsp;&nbsp; "
                    f"<span style='color:#4ADE80; font-weight:700;'>🔮 Prediction available</span>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"**🏏 {team1} vs {team2}** &nbsp;&nbsp; "
                    f"<span style='color:#94A3B8; font-weight:600;'>⏳ No prediction (insufficient data)</span>",
                    unsafe_allow_html=True
                )

            st.caption(f"{competition} | {kickoff}")

            # 👇 NAYA: Live score check karo
            if not live_scores_df.empty:
                live_match = live_scores_df[
                    (live_scores_df["home"].str.lower() == str(team1).lower()) &
                    (live_scores_df["away"].str.lower() == str(team2).lower())
                ]
                if not live_match.empty:
                    lm = live_match.iloc[0]
                    st.markdown(f"""
                    <div style="background:#1a2e1a; border:1px solid #22C55E; border-radius:10px; padding:12px; margin:8px 0;">
                        <b style="color:#4ADE80;">🔴 LIVE</b><br>
                        {team1}: <b>{lm['score_team1']}</b><br>
                        {team2}: <b>{lm['score_team2']}</b><br>
                        <i style="color:#94A3B8;">{lm['status']}</i>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
    # =================================================
    # SECTION 2 — PREDICTABLE MATCHES (expandable)
    # =================================================
    st.markdown(
        '<div class="section-title">🔮 Predictable Matches</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Only matches where BOTH teams have played at least 2 previous "
        "matches (win or loss) are shown here."
    )

    if predictions_df.empty:
        st.info(
            "No upcoming match currently has enough team history for a "
            "prediction. Both teams need at least 2 previous matches."
        )
    else:
        st.success(
            f"✅ **{total_predictions}** match(es) have predictions ready. "
            f"Click below to see predictions."
        )

        # -------- Expandable card style for each prediction --------
        for _, match in predictions_df.iterrows():

            # Header line: teams + predicted winner
            header = (
                f"🏏 {match['team1']} vs {match['team2']}  —  "
                f"Predicted: {match['predicted_winner']}"
            )

            with st.expander(header, expanded=False):

                st.caption(
                    f"{match['category']} | {match['competition']} | "
                    f"{match['match_time']}"
                )

                t1, t2 = st.columns(2)

                with t1:
                    st.markdown(f"### {match['team1']}")
                    st.write(f"Recent Form: **{match['team1_recent_form']}**")
                    st.write(f"Recent Matches: **{_to_int(match['team1_recent_matches'])}**")
                    st.write(f"International Matches: **{_to_int(match['team1_international_matches'])}**")
                    st.write(f"Total History: **{_to_int(match['team1_total_history'])}**")

                with t2:
                    st.markdown(f"### {match['team2']}")
                    st.write(f"Recent Form: **{match['team2_recent_form']}**")
                    st.write(f"Recent Matches: **{_to_int(match['team2_recent_matches'])}**")
                    st.write(f"International Matches: **{_to_int(match['team2_international_matches'])}**")
                    st.write(f"Total History: **{_to_int(match['team2_total_history'])}**")

                # Indicative shares
                share1 = float(match["team1_estimated_share"])
                share2 = float(match["team2_estimated_share"])

                p1, p2 = st.columns(2)
                p1.metric(f"{match['team1']} indicative share", f"{share1:.2f}%")
                p2.metric(f"{match['team2']} indicative share", f"{share2:.2f}%")
                p1.progress(max(0.0, min(1.0, share1 / 100)))
                p2.progress(max(0.0, min(1.0, share2 / 100)))

                st.markdown(f"""
                <div class="prediction-card">
                    <div style="color:#94A3B8; font-size:13px; font-weight:700;">
                        PREDICTED WINNER
                    </div>
                    <div style="font-size:40px; margin:12px 0;">🏆</div>
                    <div class="winner-text">{match["predicted_winner"]}</div>
                    <div style="color:#CBD5E1; margin-top:8px;">
                        Based on recent + international form
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.info(f'Data Confidence: {match["data_confidence"]}')

                st.caption(
                    "Recent-form estimates are not guaranteed outcomes or "
                    "validated machine-learning probabilities."
                )

        # -------- Summary table --------
        st.markdown(
            '<div class="section-title">📋 Predictions Summary</div>',
            unsafe_allow_html=True
        )
        st.dataframe(predictions_df, use_container_width=True, hide_index=True)
# =====================================================
# 8. TEAM STATISTICS PAGE
# =====================================================

elif page == "📊 Team Statistics":

    st.markdown(
        '<div class="main-title">📊 Team Performance Center</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Explore historical records and performance of individual teams.</div>',
        unsafe_allow_html=True
    )

    selected_team = st.selectbox(
        "SELECT YOUR TEAM",
        teams
    )

    team_matches = df[
        (df["team1"] == selected_team) |
        (df["team2"] == selected_team)
    ].copy()

    total_matches = len(team_matches)

    wins = len(
        team_matches[
            team_matches["winner"] == selected_team
        ]
    )

    losses = total_matches - wins

    win_percentage = (
        (wins / total_matches) * 100
        if total_matches > 0 else 0
    )

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    statistics = [
        ("MATCHES PLAYED", total_matches),
        ("MATCHES WON", wins),
        ("MATCHES NOT WON", losses),
        ("WIN PERCENTAGE", f"{win_percentage:.1f}%")
    ]

    for col, (label, value) in zip(
        [col1, col2, col3, col4], statistics
    ):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    chart1, chart2 = st.columns(2)

    with chart1:

        st.markdown(
            '<div class="section-title">🏆 Wins vs Not Won</div>',
            unsafe_allow_html=True
        )

        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("#17243A")
        ax.set_facecolor("#17243A")

        ax.pie(
            [wins, losses],
            labels=["Won", "Not Won"],
            autopct="%1.1f%%",
            startangle=90,
            colors=["#22C55E", "#475569"],
            textprops={"color": "white"}
        )

        st.pyplot(fig)
        plt.close(fig)

    with chart2:

        st.markdown(
            '<div class="section-title">📈 Yearly Matches</div>',
            unsafe_allow_html=True
        )

        yearly_matches = team_matches.groupby("year").size()

        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("#17243A")
        ax.set_facecolor("#17243A")

        yearly_matches.plot(
            kind="bar",
            ax=ax,
            color="#38BDF8"
        )

        ax.set_xlabel("Year", color="white")
        ax.set_ylabel("Matches", color="white")
        ax.tick_params(colors="white")
        ax.grid(axis="y", alpha=0.15)

        st.pyplot(fig)
        plt.close(fig)

    st.markdown("---")

    st.markdown(
        '<div class="section-title">📋 Match History</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        team_matches[
            ["date", "team1", "team2", "winner", "city"]
        ].sort_values(
            "date",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# =====================================================
# 9. ABOUT PROJECT PAGE
# =====================================================

elif page == "ℹ️ About Project":

    st.markdown(
        '<div class="main-title">ℹ️ About Cricket IQ</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Project information, methodology and technologies.</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
        <h2>🏏 Cricket Match Analysis and Outcome Prediction</h2>
        <p>
        This project analyzes historical ICC Men's T20 World Cup data
        and applies Machine Learning to predict possible match winners.
        </p>
        <p>
        Users enter match details after the toss, and the trained
        Logistic Regression model generates a prediction.
        </p>
        <p>
        The upcoming match module uses recent team performance
        to estimate outcomes of future Men's T20 fixtures.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">🛠️ Technologies Used</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    col1.markdown("""
    <div class="metric-card">
        <div class="metric-value">Python</div>
        <div class="metric-label">Programming Language</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown("""
    <div class="metric-card">
        <div class="metric-value">Pandas</div>
        <div class="metric-label">Data Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown("""
    <div class="metric-card">
        <div class="metric-value">Streamlit</div>
        <div class="metric-label">Web Application</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.markdown("""
    <div class="metric-card">
        <div class="metric-value">Matplotlib</div>
        <div class="metric-label">Data Visualization</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown("""
    <div class="metric-card">
        <div class="metric-value">Scikit-learn</div>
        <div class="metric-label">Machine Learning</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown("""
    <div class="metric-card">
        <div class="metric-value">Joblib</div>
        <div class="metric-label">Model Saving</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">🧠 Machine Learning Details</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
        <p><b>Historical Model:</b> Logistic Regression</p>
        <p><b>Compared Algorithm:</b> Random Forest</p>
        <p><b>Historical Test Accuracy:</b> 67.39%</p>
        <p><b>Historical Dataset:</b> ICC Men's T20 World Cup data from Cricsheet</p>
        <p><b>Historical Prediction Type:</b> Binary Classification</p>
        <p><b>Upcoming Prediction:</b> Recent-form-based estimates</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">⚙️ Project Workflow</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
        <p>01 — Data Collection</p>
        <p>02 — Data Cleaning and Preprocessing</p>
        <p>03 — Exploratory Data Analysis</p>
        <p>04 — Feature Selection and Encoding</p>
        <p>05 — Train-Test Split</p>
        <p>06 — Model Training and Comparison</p>
        <p>07 — Model Evaluation</p>
        <p>08 — Historical Match Winner Prediction</p>
        <p>09 — Upcoming Match Data Collection</p>
        <p>10 — Recent Team Form Analysis</p>
        <p>11 — Upcoming Match Prediction</p>
        <p>12 — Streamlit Web Application</p>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 10. FOOTER
# =====================================================

st.markdown("""
<div class="footer">
    🏏 CRICKET IQ | CRICKET MATCH ANALYSIS & PREDICTION
    <br><br>
    Powered by Python, Machine Learning and Streamlit
</div>
""", unsafe_allow_html=True)