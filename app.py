import streamlit as st
from data_loader import load_matches, load_players, load_goalkeeping
import plotly.express as px
import pandas as pd
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def data_matches():
    matches = load_matches()
    completed = matches[matches["Record"] != "No Match"]
    st.subheader("Matches Data")
    st.dataframe(completed.head())

def data_players():
    players = load_players()
    st.subheader("Players Data")
    st.dataframe(players)

def data_goalkeeping():
    goalkeeping = load_goalkeeping()
    st.subheader("Goalkeeping Data")
    st.dataframe(goalkeeping.head())

st.set_page_config(page_title="Senegal Scout ", layout="wide")

page = st.sidebar.radio("Navigate", [
    "Overview",
    "Tactical Identity", 
    "Player Spotlight"
])

if page == "Overview":
    st.title(" Senegal — Pre WC 2026 Scout Report")
    
    matches = load_matches()
    completed = matches[matches["Record"] != "No Match"]
    
    wins = len(completed[completed["Record"] == "Win"])
    goals_scored = int(completed["GF"].sum())
    clean_sheets = len(completed[completed["GA"] == 0])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Wins", wins)
    col2.metric("Goals Scored", goals_scored)
    col3.metric("Clean Sheets", clean_sheets)
    st.subheader("Recent Form")
    last_10 = completed.tail(10)
    colors = {"Win": "green", "Draw": "gray", "Loss": "red"}
    badges = ""
    for _, row in last_10.iterrows():
        color = colors[row["Record"]]
        label = row["Record"][0]  # Just W, D or L
        opponent = row["Opponent"]
        badges = '<div style="display:flex; flex-wrap:wrap; gap:8px;">'
    for _, row in last_10.iterrows():
            color = colors[row["Record"]]
            label = row["Record"][0]
            opponent = row["Opponent"]
            badges += f'<span style="background-color:{color}; color:white; padding:6px 12px; border-radius:4px; font-weight:bold;" title="{opponent}">{label}</span>'
    badges += '</div>'

    st.markdown(badges, unsafe_allow_html=True)
    st.subheader("World Cup 2026 Fixtures")
    upcoming = matches[matches["Comp"] == "World Cup"][["Date", "Opponent", "Venue"]]
    upcoming["Date"] = upcoming["Date"].dt.strftime("%d %b %Y")
    st.dataframe(upcoming, hide_index=True, use_container_width=True)

    players = load_players()
    players["Gls"] = pd.to_numeric(players["Gls"], errors="coerce")
    top_scorers = players[players["Gls"] > 0].sort_values("Gls", ascending=False).head(5)
    st.subheader("Top Scorers")
    col_left, col_right = st.columns(2)
    with col_left:
        fig_pie = px.pie(last_10, names='Record', title='Last 10 Matches Record', 
                     color='Record', color_discrete_map=colors)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        fig_scorers = px.bar(top_scorers.sort_values("Gls", ascending=True), x="Gls", y="Name", orientation="h",
                         title="Top Scorers", color_discrete_sequence=["green"])
        st.plotly_chart(fig_scorers, use_container_width=True)

elif page == "Tactical Identity":
    st.title(" Tactical Identity")
    matches = load_matches()
    completed = matches[matches["Record"] != "No Match"]
    xi = pd.DataFrame([
    {"Name": "Mendy",      "primary_pos": "GK", "x": 5,  "y": 40},
    {"Name": "Jakobs",     "primary_pos": "DF", "x": 25, "y": 10},
    {"Name": "Niakhate",   "primary_pos": "DF", "x": 25, "y": 27},
    {"Name": "Koulibaly",  "primary_pos": "DF", "x": 25, "y": 53},
    {"Name": "Diatta",     "primary_pos": "DF", "x": 25, "y": 70},
    {"Name": "I. Gueye",      "primary_pos": "DM", "x": 40, "y": 40},
    {"Name": "L. Camara",     "primary_pos": "MF", "x": 60, "y": 10},
    {"Name": "P.M. Sarr",  "primary_pos": "MF", "x": 60, "y": 27},
    {"Name": "I. Sarr",    "primary_pos": "MF", "x": 60, "y": 53},
    {"Name": "Ndiaye",     "primary_pos": "MF", "x": 60, "y": 70},
    {"Name": "Mané",       "primary_pos": "FW", "x": 80, "y": 40},
])
    pitch = Pitch(pitch_color='grass', line_color='white')
    fig_pitch, ax = pitch.draw(figsize=(3, 3))


    for _, player in xi.iterrows():
        ax.plot(player["x"], player["y"], 'o', color='yellow', markersize=10, zorder=3)
        ax.text(player["x"], player["y"] - 5, player["Name"], ha='center',
            color='white', fontsize=5, fontweight='bold')

    st.subheader("Predicted Starting XI — 4-1-4-1")
    st.pyplot(fig_pitch)

    st.subheader("Campaign Analysis")
    col_left, col_right,col_center = st.columns(3)
    formation_counts = completed["Formation"].value_counts().reset_index()
    formation_counts.columns = ["Formation", "Count"]
    with col_left:
        fig_formation = px.bar(formation_counts, x="Formation", y="Count", title="Formations Used",
                           color_discrete_sequence=["green"])
        st.plotly_chart(fig_formation, use_container_width=True)
    with col_center:
        home_away = completed.groupby(['Venue', 'Record']).size().reset_index(name='Count')
        fig_home_away = px.bar(home_away, x='Venue', y='Count', color='Record', title='Home vs Away Performance',
                            color_discrete_map={"Win": "green", "Draw": "gray", "Loss": "red"})
        st.plotly_chart(fig_home_away, use_container_width=True)
    with col_right:
        goals_over_time = completed[["Date", "GF", "GA"]].melt(id_vars="Date", var_name="Type", value_name="Goals")
        fig_goals_time=px.line(goals_over_time, x="Date", y="Goals", color="Type", title="Goals Scored vs Conceded Over Time",
                color_discrete_map={"GF": "green", "GA": "red"})
        st.plotly_chart(fig_goals_time, use_container_width=True)
  

elif page == "Player Spotlight":
    st.title(" Player Spotlight")
    players = load_players()
    for col in ["Gls", "Ast", "PPM", "onG", "onGA"]:
        players[col] = pd.to_numeric(players[col], errors="coerce")
    selected_player = st.selectbox("Select a Player", players["Name"])
    player_data = players[players["Name"] == selected_player].iloc[0]
    st.metric("Player Name", selected_player)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Appearances", player_data["MP"])
    col2.metric("Minutes", player_data["Min"])
    col3.metric("Goals", player_data["Gls"])
    col4.metric("Assists", player_data["Ast"])
    players["Gls"] = pd.to_numeric(players["Gls"], errors="coerce")
    players["Ast"] = pd.to_numeric(players["Ast"], errors="coerce")
    players["90s"] = pd.to_numeric(players["90s"], errors="coerce")
    players["PPM"] = pd.to_numeric(players["PPM"], errors="coerce")
    players["onG"] = pd.to_numeric(players["onG"], errors="coerce")

    squad_avg = players[["Gls", "Ast", "PPM", "onG"]].mean()
    player_vals = player_data[["Gls", "Ast", "PPM", "onG"]]
    categories = ["Goals", "Assists", "PPM", "Goals While On Pitch"]
    def normalize(val, min_val, max_val):
        if max_val == min_val:
            return 0
        return round((val - min_val) / (max_val - min_val) * 10, 2)

    pos = player_data["Pos"].split(",")[0]

    players["onGA"] = pd.to_numeric(players["onGA"], errors="coerce")

# precompute min/max for normalization
    gls_min, gls_max = players["Gls"].min(), players["Gls"].max()
    ast_min, ast_max = players["Ast"].min(), players["Ast"].max()
    ppm_min, ppm_max = players["PPM"].min(), players["PPM"].max()
    ong_min, ong_max = players["onG"].min(), players["onG"].max()
    onga_min, onga_max = players["onGA"].min(), players["onGA"].max()

    squad_avg = players[["Gls", "Ast", "PPM", "onG", "onGA"]].mean()

    if pos == "GK":
        categories = ["PPM", "Goals While On", "Goals Conceded While On"]
        p_vals = [normalize(player_data["PPM"], ppm_min, ppm_max),
                normalize(player_data["onG"], ong_min, ong_max),
                normalize(player_data["onGA"], onga_min, onga_max)]
        a_vals = [normalize(squad_avg["PPM"], ppm_min, ppm_max),
                normalize(squad_avg["onG"], ong_min, ong_max),
                normalize(squad_avg["onGA"], onga_min, onga_max)]

    elif pos == "DF":
        categories = ["Assists", "PPM", "Goals While On", "Goals Conceded While On"]
        p_vals = [normalize(player_data["Ast"], ast_min, ast_max),
                normalize(player_data["PPM"], ppm_min, ppm_max),
                normalize(player_data["onG"], ong_min, ong_max),
                normalize(player_data["onGA"], onga_min, onga_max)]
        a_vals = [normalize(squad_avg["Ast"], ast_min, ast_max),
                normalize(squad_avg["PPM"], ppm_min, ppm_max),
                normalize(squad_avg["onG"], ong_min, ong_max),
                normalize(squad_avg["onGA"], onga_min, onga_max)]

    elif pos == "MF":
        categories = ["Goals", "Assists", "PPM", "Goals While On"]
        p_vals = [normalize(player_data["Gls"], gls_min, gls_max),
                normalize(player_data["Ast"], ast_min, ast_max),
                normalize(player_data["PPM"], ppm_min, ppm_max),
                normalize(player_data["onG"], ong_min, ong_max)]
        a_vals = [normalize(squad_avg["Gls"], gls_min, gls_max),
                normalize(squad_avg["Ast"], ast_min, ast_max),
                normalize(squad_avg["PPM"], ppm_min, ppm_max),
                normalize(squad_avg["onG"], ong_min, ong_max)]

    else:  # FW
        categories = ["Goals", "Assists", "PPM", "Goals While On"]
        p_vals = [normalize(player_data["Gls"], gls_min, gls_max),
                normalize(player_data["Ast"], ast_min, ast_max),
                normalize(player_data["PPM"], ppm_min, ppm_max),
                normalize(player_data["onG"], ong_min, ong_max)]
        a_vals = [normalize(squad_avg["Gls"], gls_min, gls_max),
                normalize(squad_avg["Ast"], ast_min, ast_max),
                normalize(squad_avg["PPM"], ppm_min, ppm_max),
                normalize(squad_avg["onG"], ong_min, ong_max)]

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=p_vals, theta=categories, fill='toself',
        name=selected_player, line_color='green'
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=a_vals, theta=categories, fill='toself',
        name='Squad Average', line_color='gray'
    ))

    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                            title="Player vs Squad Average")
    st.plotly_chart(fig_radar, use_container_width=True)