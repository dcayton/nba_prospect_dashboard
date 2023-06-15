import pandas as pd
import numpy as np
import scrape_functions as sf

ncaa_players = sf.retrieve_bt_stats(2010, 2023)
nba_players = sf.load_bbref_data(2001, 2023)

# +
nba_ids = pd.read_csv("nba_stats_v0.csv")

nba_ids.columns = nba_ids.columns.str[4:]
nba_ids = nba_ids.drop("Pos", axis=1)
nba_ids = nba_ids[["Player", "Age", "Tm", "G", "GS", "Player-additional", "Season"]]

nba_players = nba_players.merge(nba_ids, how="inner", on=nba_ids.columns.drop("Player-additional").tolist())
# -

ncaa_players.to_csv("ncaa_players.csv", index=False)
nba_players.to_csv("nba_players.csv", index=False)


