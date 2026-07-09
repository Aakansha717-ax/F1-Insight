import os
import streamlit as st
import fastf1
import plotly.express as px
import plotly.graph_objects as go

os.makedirs("cache", exist_ok=True)

TEAM_COLORS = {
    "McLaren": "#FF8000",
    "Ferrari": "#DC0000",
    "Red Bull Racing": "#3671C6",
    "Mercedes": "#27F4D2",
    "Aston Martin": "#229971",
    "Williams": "#64C4FF",
    "Alpine": "#0090FF",
    "RB": "#6692FF",
    "Kick Sauber": "#52E252",
    "Haas F1 Team": "#B6BABD"
}
TRACK_IMAGES = {
    "Bahrain": "tracks/bahrain.png",
    "Saudi Arabia": "tracks/saudi_arabia.png",
    "Australia": "tracks/australia.png",
    "Japan": "tracks/japan.png",
    "Monaco": "tracks/monaco.png",
    "Spain": "tracks/spain.png",
    "Canada": "tracks/canada.png",
    "Austria": "tracks/austria.png",
    "Great Britain": "tracks/great_britain.png"
}
# -------------------------------
# FastF1 Cache
# -------------------------------
fastf1.Cache.enable_cache("cache")

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="F1 Insight",
    page_icon="🏎️",
    layout="wide"
)

# -------------------------------
# Load Race Data (Cached)
# -------------------------------
@st.cache_data(show_spinner="Loading Formula 1 data...")
def load_race_data(season, race):
    session = fastf1.get_session(season, race, "R")
    session.load()
    return session

# -------------------------------
# Title
# -------------------------------
st.title("🏎️ F1 Insight")
st.subheader("Formula 1 Analytics Dashboard")

st.divider()

# -------------------------------
# User Selection
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    season = st.selectbox(
        "Select Season",
        [2025, 2024, 2023, 2022]
    )

with col2:
    race = st.selectbox(
        "Select Grand Prix",
        [
            "Bahrain",
            "Saudi Arabia",
            "Australia",
            "Japan",
            "Monaco",
            "Spain",
            "Canada",
            "Austria",
            "Great Britain"
        ]
    )

left, right = st.columns([2, 1])
with right:
    st.subheader("🗺️ Circuit Map")

    st.image(
        TRACK_IMAGES[race],
        caption=f"{race} Grand Prix Circuit",
        use_container_width=True
    )
# -------------------------------
# Load Session
# -------------------------------
session = load_race_data(season, race)

results = session.results

# -------------------------------
# Leaderboard
# -------------------------------
display_results = results[
    [
        "Position",
        "FullName",
        "TeamName",
        "GridPosition",
        "Points",
        "Status",
        "Laps"
    ]
]

st.subheader("🏁 Race Leaderboard")

st.dataframe(
    display_results,
    use_container_width=True
)

# -------------------------------
# Podium
# -------------------------------
st.divider()

st.subheader("🏆 Podium")

top3 = display_results.head(3)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🥇 Winner",
        top3.iloc[0]["FullName"],
        top3.iloc[0]["TeamName"]
    )

with col2:
    st.metric(
        "🥈 Second",
        top3.iloc[1]["FullName"],
        top3.iloc[1]["TeamName"]
    )

with col3:
    st.metric(
        "🥉 Third",
        top3.iloc[2]["FullName"],
        top3.iloc[2]["TeamName"]
    )

# -------------------------------
# Lap Time Analysis
# -------------------------------
st.divider()

st.subheader("📈 Lap Time Analysis")

drivers = sorted(session.laps["Driver"].unique())

col1, col2 = st.columns(2)

with col1:
    driver1 = st.selectbox(
        "Driver 1",
        drivers
    )

with col2:
    driver2 = st.selectbox(
        "Driver 2",
        drivers,
        index=1
    )

driver1_laps = session.laps.pick_drivers(driver1)
driver2_laps = session.laps.pick_drivers(driver2)

driver1_laps = driver1_laps.pick_quicklaps().copy()
driver2_laps = driver2_laps.pick_quicklaps().copy()

driver1_laps["LapTimeSeconds"] = (
    driver1_laps["LapTime"].dt.total_seconds()
)

driver2_laps["LapTimeSeconds"] = (
    driver2_laps["LapTime"].dt.total_seconds()
)
team1 = results.loc[
    results["Abbreviation"] == driver1,
    "TeamName"
].values[0]

team2 = results.loc[
    results["Abbreviation"] == driver2,
    "TeamName"
].values[0]
color1 = TEAM_COLORS.get(team1, "white")
color2 = TEAM_COLORS.get(team2, "white")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
    x=driver1_laps["LapNumber"],
    y=driver1_laps["LapTimeSeconds"],
    mode="lines+markers",
    name=driver1,
    line=dict(color=color1, width=3)
)
)

fig.add_trace(
    go.Scatter(
    x=driver2_laps["LapNumber"],
    y=driver2_laps["LapTimeSeconds"],
    mode="lines+markers",
    name=driver2,
    line=dict(color=color2, width=3)
)
)

fig.update_layout(
    title="🏎️ Driver Lap Time Comparison",
    template="plotly_dark",
    hovermode="x unified",
    xaxis_title="Lap Number",
    yaxis_title="Lap Time (Seconds)",
    legend_title="Drivers"
)
st.divider()
st.subheader("🛞 Tyre Strategy")
tyre_data = driver1_laps[
    ["LapNumber", "Compound"]
].copy()
fig_tyres = px.scatter(
    tyre_data,
    x="LapNumber",
    y="Compound",
    color="Compound",
    title=f"{driver1} Tyre Strategy"
)

st.plotly_chart(
    fig_tyres,
    use_container_width=True
)
st.divider()
st.subheader("📊 Race Statistics")
fastest = driver1_laps["LapTimeSeconds"].min()

st.metric(
    "⚡ Fastest Lap",
    f"{fastest:.3f} s"
)
average = driver1_laps["LapTimeSeconds"].mean()

st.metric(
    "📈 Average Lap",
    f"{average:.3f} s"
)
laps = len(driver1_laps)

st.metric(
    "🏁 Laps Completed",
    laps
)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "⚡ Fastest Lap",
        f"{fastest:.3f} s"
    )

with col2:
    st.metric(
        "📈 Average Lap",
        f"{average:.3f} s"
    )

with col3:
    st.metric(
        "🏁 Completed Laps",
        laps
    )
st.divider()
st.subheader("🏁 Race Insights")
winner = display_results.iloc[0]
display_results = display_results.copy()

display_results["PositionsGained"] = (
    display_results["GridPosition"] - display_results["Position"]
)

biggest_gain = display_results.loc[
    display_results["PositionsGained"].idxmax()
]
fastest_driver = None
fastest_time = float("inf")
fastest_lap = None

for driver in drivers:

    laps = session.laps.pick_drivers(driver).pick_quicklaps()

    if laps.empty:
        continue

    best = laps["LapTime"].min()

    if best.total_seconds() < fastest_time:

        fastest_time = best.total_seconds()

        driver_name = results.loc[
        results["Abbreviation"] == driver,
        "FullName"
        ].values[0]

        fastest_driver = driver_name

        fastest_lap = laps.loc[
            laps["LapTime"] == best,
            "LapNumber"
        ].iloc[0]

st.info(f"""
🏆 **Winner:** {winner['FullName']} ({winner['TeamName']})

🚀 **Biggest Position Gain:** {biggest_gain['FullName']}
(+{int(biggest_gain['PositionsGained'])} places)

⚡ **Fastest Lap:** {fastest_driver}
on Lap {int(fastest_lap)}
({fastest_time:.3f} sec)
""")

st.plotly_chart(fig, use_container_width=True)


st.success("Race data loaded successfully!")

st.write(f"Selected Season: **{season}**")
st.write(f"Selected Race: **{race}**")