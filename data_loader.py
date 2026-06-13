import pandas as pd

def RecordMatches(row):
    if pd.isnull(row["GF"]) and pd.isnull(row["GA"]):
        return "No Match"
    if row["GF"] > row["GA"]:
        return "Win"
    elif row["GF"] < row["GA"]:
        return "Loss"
    else:
        return "Draw"

def load_matches():
    matches = pd.read_csv("data/matches.csv", parse_dates=["Date"], dayfirst=True)
    matches["Record"] = matches.apply(RecordMatches, axis=1)
    matches["Formation"] = matches["Formation"].replace({"05/04/2001": "5-4-1", "03/04/2003": "3-4-3"})
    matches["Opp Formation"] = matches["Opp Formation"].replace({"03/04/2003": "3-4-3"})
    return matches

def load_players():
    players_standard = pd.read_csv("data/players_standard.csv",encoding="latin-1")
    players_standard=players_standard[players_standard["Name"].notna()&(players_standard["Name"]!="Player")]
    players_standard["MP"] = pd.to_numeric(players_standard["MP"], errors="coerce")
    players_standard = players_standard[players_standard["MP"] > 0]
    players_standard = players_standard.drop(columns=["Gls.1", "Ast.1", "G+A.1", "G-PK.1", "G+A-PK"])
    players_playing_time = pd.read_csv("data/players_playing_time.csv",encoding="latin-1",header=1)
    players_playing_time = players_playing_time[players_playing_time["Player"].notna() & (players_playing_time["Player"] != "Player")]
    players_playing_time = players_playing_time.rename(columns={"Player": "Name"})
    players_playing_time["MP"] = pd.to_numeric(players_playing_time["MP"], errors="coerce")
    players_playing_time = players_playing_time[players_playing_time["MP"] > 0]
    players_playing_time = players_playing_time[["Name", "PPM", "onG", "onGA"]]
    players=pd.merge(players_standard, players_playing_time, on="Name", how="inner")
    return players

def load_goalkeeping():
    goalkeeping = pd.read_csv("data/players_goalkeeper.csv",encoding="latin-1",header=1)
    goalkeeping=goalkeeping[goalkeeping["Player"].notna()&(goalkeeping["Player"]!="Player")]
    goalkeeping = goalkeeping.rename(columns={"Player": "Name"})
    goalkeeping["MP"] = pd.to_numeric(goalkeeping["MP"], errors="coerce")
    goalkeeping = goalkeeping[goalkeeping["MP"] > 0]
    return goalkeeping

print(load_players())
print(load_goalkeeping())