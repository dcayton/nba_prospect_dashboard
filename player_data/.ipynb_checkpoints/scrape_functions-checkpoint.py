import numpy as np
import pandas as pd


def ncaa_poss_pull(start_year, end_year):
    """
    Returns dataframe of all average possessions 
    for D1 teams between start year and end year.
    (Where year denotes the (year-1)-(year) season)
    """
    possessions = pd.DataFrame()
    for year in np.arange(start_year, (end_year+1)):
        teams = pd.read_html(f"https://www.sports-reference.com/cbb/seasons/men/{year}-school-stats.html")[0]
        stats = teams["Totals"]
        
        teams.columns = teams.columns.droplevel(level=0)
        teams = pd.concat([teams[["School", "G"]], stats], axis=1)
        
        for c in teams.columns:
            if "Unnamed" in c:
                teams = teams.drop(c, axis=1)
            else:
                pass
        
        teams = teams[(teams["School"].notna()) & (teams["School"]!="School") & (teams["G"]!="0")]
        teams.iloc[:,1:] = teams.iloc[:,1:].astype(float)
        
        teams["possessions"] = (teams.FGA - teams.ORB + teams.TOV + (.45 * teams.FTA)) / teams.G
        teams["School"] = [s[:-5] if "\xa0NCAA" in s else s for s in teams.School.tolist()]
        teams["ssid"] = teams.School + f"_{year}"
        
        teams = teams[["ssid", "possessions"]]
        possessions = pd.concat([possessions, teams], axis=0, ignore_index=True)
    return possessions

def bart_torvik_format(df):
    c_to_drop = ["ncaa_num", "ncaa_player_id", "ncaa_type", "ncaa_role", "ncaa_last_col"]
    df = df.drop(c_to_drop, axis=1)
    
    df["ncaa_minutes_%"] = np.round((df["ncaa_minutes_%"] / 100), 3)
    df.iloc[:, 6:13] = np.round((df.iloc[:, 6:13] / 100), 3)
    df.iloc[:, 22:25] = np.round((df.iloc[:, 22:25] / 100), 3)
    
    df = df[df.ncaa_ht.str[0].isin(["5", "6", "7"])]
    df.ncaa_ht.str.replace("'", "-")
    df.ncaa_ht = (df.ncaa_ht.str[0].astype(int) * 12) + (df.ncaa_ht.str[2:].astype(int))
    
    na_zero_cols = df.columns[df.isnull().sum() > 100]
    df[na_zero_cols] = df[na_zero_cols].fillna(0)
    
    df = df.dropna(axis=0, how="any")
    
    per_game_columns = ["ncaa_ftm", "ncaa_fta", "ncaa_2pm", "ncaa_2pa", 
                        "ncaa_3pm", "ncaa_3pa", "ncaa_rim_makes", "ncaa_rim_att",
                        "ncaa_mid_range_makes", "ncaa_mid_range_att", 
                        "ncaa_dunks_made", "ncaa_dunks_att"
                       ]
    for c in per_game_columns:
        df[c] = df[c] / df.ncaa_gp

    df["ncaa_fga"] = df.ncaa_2pa + df.ncaa_3pa
    df["ncaa_tov"] = ((1 / df.ncaa_ast_tov_ratio) * df.ncaa_ast).replace(np.inf, np.nan).fillna(0)
    df["ncaa_ppp"] = df.ncaa_pts / (df.ncaa_fga + df.ncaa_tov + (.44 * df.ncaa_fta))
    
    df["ncaa_rim_prop"] = (df.ncaa_rim_att / df.ncaa_fga).replace(np.inf, np.nan).fillna(0)
    df["ncaa_mid_prop"] = (df.ncaa_mid_range_att / df.ncaa_fga).replace(np.inf, np.nan).fillna(0)
    df["ncaa_3pt_prop"] = (df.ncaa_3pa / df.ncaa_fga).replace(np.inf, np.nan).fillna(0)
    
    df["ncaa_ast_fg_ratio"] = (df.ncaa_ast / df.ncaa_fga).replace(np.inf, np.nan).fillna(0)
    df = df[df["ncaa_minutes_%"] > .2]
    return df

def retrieve_bt_stats(start_year, end_year):
    players = pd.DataFrame()
    
    for year in np.arange(start_year, (end_year+1)):
        pldf = pd.read_csv(f"http://barttorvik.com/getadvstats.php?year={year}&csv=1",
                                    names=['ncaa_player_name', 'ncaa_team', 'ncaa_conf', 
                                           'ncaa_gp', 'ncaa_minutes_%', 'ncaa_ortg', 'ncaa_usg', 
                                           'ncaa_efg%', 'ncaa_ts%', 'ncaa_oreb%', 'ncaa_dreb%', 
                                           'ncaa_ast%', 'ncaa_to%', 'ncaa_ftm', 'ncaa_fta', 
                                           'ncaa_ft%', 'ncaa_2pm', 'ncaa_2pa', 'ncaa_2p%',
                                           'ncaa_3pm', 'ncaa_3pa', 'ncaa_3p%', 'ncaa_blk%', 
                                           'ncaa_stl%', 'ncaa_ftr', 'ncaa_yr', 'ncaa_ht', 
                                           'ncaa_num', 'ncaa_porpag', 'ncaa_adjoe', 
                                           'ncaa_foul_rate', 'ncaa_year', 'ncaa_player_id', 
                                           'ncaa_type', 'ncaa_recruit_rank', 'ncaa_ast_tov_ratio',
                                           'ncaa_rim_makes', 'ncaa_rim_att', 
                                           'ncaa_mid_range_makes', 'ncaa_mid_range_att',
                                           'ncaa_rim_fg%', 'ncaa_mid_fg%', 'ncaa_dunks_made', 
                                           'ncaa_dunks_att', 'ncaa_dunk_fg%', 'ncaa_draft_pick', 
                                           'ncaa_drtg', 'ncaa_adrtg', 'ncaa_dporpag', 
                                           'ncaa_stops', 'ncaa_bpm', 'ncaa_obpm', 'ncaa_dbpm', 
                                           'ncaa_gbpm', 'ncaa_min_per_game', 'ncaa_ogbpm', 'ncaa_dgbpm', 
                                           'ncaa_oreb', 'ncaa_dreb', 'ncaa_treb', 'ncaa_ast', 'ncaa_stl', 
                                           'ncaa_blk', 'ncaa_pts', "ncaa_role", "ncaa_last_col"]
                                    )
        pldf = bart_torvik_format(pldf)
        players = pd.concat([players, pldf], axis=0, ignore_index=True)
    return players

def possession_merge(ssid_poss_df, ncaa_players_df):
    df = ncaa_players_df.merge(ssid_poss_df, how="inner", on="ssid")
    return df


def format_bbref_basic(bbref, year_start):
    """
    Formats bbref dataframes into standardized forms
    
    bbref: Dataframe of basketball reference player data
    year: season you want to obtain player data from (year-year+1)
    """
    bbref = bbref.loc[bbref.Rk!="Rk"]
    bbref = bbref.drop_duplicates(subset=["Rk", "Player", "Pos", "Age"], keep="first")
    
    unnamed_columns = [c for c in bbref.columns.tolist() if "Unnamed" in c]
    bbref = bbref.drop(unnamed_columns+["Rk"], axis=1).reset_index(drop=True)
    
    bbref_cols = ["Age"] + bbref.iloc[:, 4:].columns.tolist()
    bbref[bbref_cols] = bbref[bbref_cols].apply(pd.to_numeric)
    
    bbref["AST_2_TOV"] = (bbref.AST / bbref.TOV).replace(np.inf, np.nan).fillna(0)
    bbref["AST_2_FG"] = (bbref.AST / bbref.FGA).replace(np.inf, np.nan).fillna(0)
    
    possessions = bbref.FGA + bbref.TOV + (.45 * bbref.FTA)
    bbref["PPP"] = (bbref.PTS / possessions).replace(np.inf, np.nan).fillna(0)
    
    bbref["Season"] = year_start
    return bbref


def format_bbref_adv(bbref, year_start):
    """
    Formats bbref advanced dataframes into standardized forms
    
    bbref: Dataframe of basketball reference player data
    year: season you want to obtain player data from (year-year+1)
    """
    bbref = bbref.loc[bbref.Rk!="Rk"]
    bbref = bbref.drop_duplicates(subset=["Rk", "Player", "Pos", "Age"], keep="first")
    
    unnamed_columns = [c for c in bbref.columns.tolist() if "Unnamed" in c]
    bbref = bbref.drop(unnamed_columns+["Rk"], axis=1).reset_index(drop=True)
    
    bbref_cols = ["Age"] + bbref.iloc[:, 4:].columns.tolist()
    bbref[bbref_cols] = bbref[bbref_cols].apply(pd.to_numeric)
    
    bbref["Season"] = year_start
    return bbref


def format_bbref_shooting(bbref, year_start):
    """
    Formats bbref shooting data into standardized dataframe
    
    bbref: Dataframe of basketball reference player data
    year: season you want to obtain player data from (year-year+1)
    """
    bbref.columns = bbref.columns.droplevel(level=0)
    
    bbref = bbref.loc[bbref.Rk!="Rk"]
    bbref = bbref.drop_duplicates(subset=["Rk", "Player", "Pos", "Age"], keep="first")
    
    u_c = [c for c in bbref.columns.tolist() if "Unnamed" in c]
    bbref = bbref.drop(u_c+["Rk"], axis=1).fillna(0)
    
    cols = bbref.columns
    c_len = len(bbref.columns)
    c_names = []

    for i in np.arange(0, c_len):
        if i < 8:
            c_name = cols[i]
            c_names += [c_name]
        elif i < 14:
            c_name = cols[i] + "_prop"
            c_names += [c_name]
        elif i < 20:
            c_name = cols[i] + "_fg%"
            c_names += [c_name]
        elif i < 22:
            c_name = cols[i] + "_%astd"
            c_names += [c_name]
        elif i < 24:
            c_name = "dunk_" + cols[i]
            c_names += [c_name]
        elif i < 26:
            c_name = "corner_" + cols[i]
            c_names += [c_name]
        else:
            c_name = "heave_" + cols[i]
            c_names += [c_name]
            
    bbref.columns = c_names
    
    bbref_cols = ["Age"] + bbref.iloc[:, 4:].columns.tolist()
    bbref[bbref_cols] = bbref[bbref_cols].apply(pd.to_numeric)
    
    bbref["Season"] = year_start
    return bbref


def load_bbref_data(start_year, end_year):
    player_data = pd.DataFrame()
    
    for year in np.arange(start_year, end_year):
        from time import sleep
        year_basic = pd.read_html(f"https://www.basketball-reference.com/leagues/NBA_{year+1}_per_poss.html")[0]
        year_adv = pd.read_html(f"https://www.basketball-reference.com/leagues/NBA_{year+1}_advanced.html")[0]
        year_shooting = pd.read_html(f"https://www.basketball-reference.com/leagues/NBA_{year+1}_shooting.html")[0]
        
        year_basic = format_bbref_basic(year_basic, year)
        year_adv = format_bbref_adv(year_adv, year)
        year_shooting = format_bbref_shooting(year_shooting, year)
        
        year_players = year_basic.merge(year_adv, how="inner", on=["Player", "Pos", "Age", "Tm", "G", "MP", "Season"])
        year_players = year_players.merge(year_shooting, how="inner", on=["Player", "Pos", "Age", "Tm", "G", "MP", "FG%", "Season"])
        
        year_players["MP"] = year_players["MP"] / year_players["G"]
        
        player_data=pd.concat([player_data, year_players], axis=0, ignore_index=True)
        sleep(5)
    
    from unidecode import unidecode
    player_data["Player"] = player_data["Player"].str.replace("*", "", regex=False)
    player_data["Player"] = player_data["Player"].apply(unidecode)
    
    return player_data


