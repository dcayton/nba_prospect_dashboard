import numpy as np
import pandas as pd

nba = pd.read_csv("nba_players.csv")
ncaa = pd.read_csv("ncaa_players.csv")
combine = pd.read_csv("combine_stats.csv")
draft_tiers = pd.read_csv("draft_rankings.csv")

pd.set_option("display.max_columns", 300)

ncaa_comb = ncaa.merge(combine, how="left", left_on=["ncaa_player_name", "ncaa_year"],
                       right_on=["PLAYER", "YEAR"]).drop(["PLAYER", "YEAR", "POS"], axis=1)

nba.columns = "rookie_" + nba.columns

rookies = nba[nba.rookie_Age<=23].merge(ncaa_comb, how="inner", 
                                        left_on=["rookie_Player", "rookie_Season"],
                                        right_on=["ncaa_player_name", "ncaa_year"]
                                       )

rookies = rookies.sort_values("ncaa_recruit_rank").drop_duplicates(subset=["rookie_Player"], keep="last", ignore_index=True)
rookies.loc[rookies.HEIGHT.isnull(), "HEIGHT"] = rookies.loc[rookies.HEIGHT.isnull(), "ncaa_ht"]

rookies = rookies.merge(draft_tiers, how="left", on=["ncaa_player_name", "ncaa_year"])
rookies["consensus_tier"] = rookies["consensus_tier"].fillna(7)


def lin_fill_na(df, fill_column_name, feature_column_list):
    test = df[df[fill_column_name].isnull()]
    train = df[df[fill_column_name].notnull()]
    
    train_x = train[feature_column_list]
    train_y = train[fill_column_name]
    
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    
    model.fit(train_x, train_y)
    
    test_x = test[feature_column_list]
    test_y_pred = model.predict(test_x)
    
    df.loc[df[fill_column_name].isnull(), fill_column_name] = np.round(test_y_pred, 1)
    return df

rookies = lin_fill_na(rookies, "WEIGHT", ["HEIGHT"])
rookies = lin_fill_na(rookies, "WINGSPAN", ["HEIGHT", "WEIGHT"])
rookies = lin_fill_na(rookies, "STANDING REACH", ["HEIGHT", "WINGSPAN"])
rookies = lin_fill_na(rookies, "STANDING VERTICAL", ["HEIGHT", "WEIGHT"])
rookies = lin_fill_na(rookies, "VERTICAL LEAP", ["HEIGHT", "WEIGHT"])
rookies = lin_fill_na(rookies, "LANE AGILITY", ["HEIGHT", "WEIGHT"])
rookies = lin_fill_na(rookies, "THREE QUARTER SPRINT", ["HEIGHT", "WEIGHT"])

rookies.to_csv("rookies.csv", index=False)

rookies

season_df[season_df.iloc[:,1]>=3].index

# +
nba = pd.read_csv("nba_players.csv")

def peak_row_create(player_frame, peak_len=3):
    player_frame = player_frame.loc[player_frame.G > 20]
    peaks_frame = player_frame.sort_values("BPM", ascending=False)[:peak_len]
    peak_series = peaks_frame.mean(axis=0, numeric_only=True)
    return np.round(peak_series, 2)

max_age_df = nba.groupby("Player-additional").max("Age")
season_df = nba.groupby("Player-additional").count()

nba_qual = nba[(nba["Player-additional"].isin(max_age_df[max_age_df.Age>=24].index.tolist() + season_df[season_df.iloc[:,1]>=4].index.tolist()))].reset_index(drop=True)

peak_stats = nba_qual.groupby("Player-additional", as_index=False).apply(peak_row_create)
peak_stats.columns = "peak_" + peak_stats.columns
peaks = peak_stats.dropna(axis=0)

ncaa_rookie_peak = rookies.merge(peaks, how="inner", left_on="rookie_Player-additional", right_on="peak_Player-additional").rename({"rookie_Age": "prospect_age"},
                                                                                                                                  axis=1)
ncaa_to_peak = ncaa_rookie_peak[ncaa_rookie_peak.columns.drop(list(ncaa_rookie_peak.filter(regex='rookie')))]

ncaa_to_peak.to_csv("ncaa_to_peak.csv", index=False)
peaks.to_csv("peaks.csv", index=False)
# -

