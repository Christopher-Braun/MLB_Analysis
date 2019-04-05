import numpy as np
import pandas as pd

master = pd.read_csv("CSV/mlb_all_players.csv", encoding='latin-1')
master2 = pd.read_csv("CSV/master2.csv", encoding='latin-1')
batters = pd.read_csv('CSV/batter_team.csv', encoding='latin-1')
pitchers = pd.read_csv('CSV/pitching_team.csv', encoding='latin-1')
scores_weather = pd.read_csv("CSV/games_by_date.csv", encoding='latin-1')
pitchers_rl = pd.read_csv('CSV/pitcher_vs_RL.csv', encoding='latin-1')

from constant_variables import TEAM_INITIALS
def get_team_ini(team_ini):
    # Change format of team initials to match mlb.com
    for name, ini in TEAM_INITIALS.items():
        if ini == team_ini:
            print(ini + ":" + team_ini + ":" + name)
            return name
        elif name == team_ini:
            print(ini + ":" + team_ini + ":" + name)
            return name
        else:
            return team_ini

from constant_variables import PLAYERS
def get_player_name(player_name):
    # Change format of team initials to match mlb.com
    i=0
    while i <= len(PLAYERS):
        for name, name1 in PLAYERS.items():
            if name1 == player_name:
                print(name1 + ":" + player_name + ":" + name)
                return name
            elif name == player_name:
                print(name1 + ":" + player_name + ":" + name)
                return name
            elif i == len(PLAYERS):
                return player_name
            else:
                i += 1
        
from constant_variables import ADD_PLAYERS
master['mlb_name'] = list(map((lambda x:get_player_name(x)), master['mlb_name']))
master['NAME_TEAM'] = master['mlb_name'] + ' ' + master['TM']

df = pd.DataFrame([['NA', player[0], 'NA', 'NA', 'NA', player[1], player[2], player[3], 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', player[4], player[5],  'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA'] for player in ADD_PLAYERS if player not in list(master2['PLAYERNAME'])] , columns = master2.columns)
master2 = pd.concat([master2, df], axis=0)
master2['TEAM'] = list(map((lambda x:get_team_ini(str(x))), master2['TEAM'].values))
pitchers_rl['NAME'] = list(map((lambda x:str(x).upper()), pitchers_rl['NAME']))
pitchers_rl['NAME'] = list(map((lambda x:get_player_name(x)), pitchers_rl['NAME'].values))

pitchers['TEAM'] = list(map((lambda x:get_team_ini(x)), pitchers['TEAM']))
pitchers['NAME'] = list(map((lambda x:get_player_name(x)), pitchers['NAME'].values))
batters['TEAM'] = list(map((lambda x:get_team_ini(x)), batters['TEAM']))
master2['PLAYERNAME'] = list(map((lambda x:str(x).upper()), master2['PLAYERNAME']))
master2['FANGRAPHSNAME'] = list(map((lambda x:str(x).upper()), master2['FANGRAPHSNAME']))
master2['MLBNAME'] = list(map((lambda x:str(x).upper()), master2['MLBNAME']))
master2['CBSNAME'] = list(map((lambda x:str(x).upper()), master2['CBSNAME']))
master2['NFBCNAME'] = list(map((lambda x:str(x).upper()), master2['NFBCNAME']))
master2['ESPNNAME'] = list(map((lambda x:str(x).upper()), master2['ESPNNAME']))
master2['YAHOONAME'] = list(map((lambda x:str(x).upper()), master2['YAHOONAME']))
master2['PLAYERNAME'] = list(map((lambda x:get_player_name(x)), master2['PLAYERNAME']))


master2['NAME_TEAM'] = master2['PLAYERNAME'] + ' ' + master2['TEAM']
master2['NAME_TEAM1'] = master2['FANGRAPHSNAME'] + ' ' + master2['TEAM']
master2['NAME_TEAM2'] = master2['MLBNAME'] + ' ' + master2['TEAM']
master2['NAME_TEAM3'] = master2['CBSNAME'] + ' ' + master2['TEAM']
master2['NAME_TEAM4'] = master2['NFBCNAME'] + ' ' + master2['TEAM']
master2['NAME_TEAM5'] = master2['ESPNNAME'] + ' ' + master2['TEAM']
master2['NAME_TEAM6'] = master2['YAHOONAME'] + ' ' + master2['TEAM']
batters['NAME_TEAM'] = batters['NAME'] + ' ' + batters['TEAM']
scores_weather['Starting_Pitcher_Home'] = list(map((lambda x:str(x).upper()), scores_weather['Starting_Pitcher_Home'].values))
scores_weather['Starting_Pitcher_Away'] = list(map((lambda x:str(x).upper()), scores_weather['Starting_Pitcher_Away'].values))
scores_weather['Starting_Pitcher_Home'] = list(map((lambda x:get_player_name(x)), scores_weather['Starting_Pitcher_Home'].values))
scores_weather['Starting_Pitcher_Away'] = list(map((lambda x:get_player_name(x)), scores_weather['Starting_Pitcher_Away'].values))
scores_weather['NAME_TEAM_AWAY'] = scores_weather['Starting_Pitcher_Away'] + ' ' + scores_weather['Away']
scores_weather['NAME_TEAM_HOME'] = scores_weather['Starting_Pitcher_Home'] + ' ' + scores_weather['Home']
master2['NAME_TEAM'] = list(map((lambda x:str(x).upper()), master2['NAME_TEAM']))
master2['NAME_TEAM1'] = list(map((lambda x:str(x).upper()), master2['NAME_TEAM1']))
master2['NAME_TEAM2'] = list(map((lambda x:str(x).upper()), master2['NAME_TEAM2']))
master2['NAME_TEAM3'] = list(map((lambda x:str(x).upper()), master2['NAME_TEAM3']))
master2['NAME_TEAM4'] = list(map((lambda x:str(x).upper()), master2['NAME_TEAM4']))
master2['NAME_TEAM5'] = list(map((lambda x:str(x).upper()), master2['NAME_TEAM5']))
master2['NAME_TEAM6'] = list(map((lambda x:str(x).upper()), master2['NAME_TEAM6']))

def name_change(df, column):
    players, not_available = [], []
    for name in df[column]:
        if name in list(master2['NAME_TEAM']):
            players.append(df['NAME'][df[column] == name].values[0])
        elif name in list(master2['NAME_TEAM1']):
            players.append(df['NAME'][df[column] == name].values[0])
        elif name in list(master2['NAME_TEAM2']):
            players.append(df['NAME'][df[column] == name].values[0])
        elif name in list(master2['NAME_TEAM3']):
            players.append(df['NAME'][df[column] == name].values[0])        
        elif name in list(master2['NAME_TEAM4']):
            players.append(df['NAME'][df[column] == name].values[0])        
        elif name in list(master2['NAME_TEAM5']):
            players.append(df['NAME'][df[column] == name].values[0])        
        elif name in list(master2['NAME_TEAM6']):
            players.append(df['NAME'][df[column] == name].values[0])
        else:
            not_available.append(df['NAME'][df[column] == name].values[0])
    return players, not_available

def name_change2(df, column, column2, column3):
    players = []
    for name in df[column]:
        if name in list(master2['NAME_TEAM']):
            players.append(master2[column2][master2['NAME_TEAM'] == name].values[0])
        elif name in list(master2['NAME_TEAM1']):
            players.append(master2[column2][master2['NAME_TEAM1'] == name].values[0])
        elif name in list(master2['NAME_TEAM2']):
            players.append(master2[column2][master2['NAME_TEAM2'] == name].values[0])
        elif name in list(master2['NAME_TEAM3']):
            players.append(master2[column2][master2['NAME_TEAM3'] == name].values[0])
        elif name in list(master2['NAME_TEAM4']):
            players.append(master2[column2][master2['NAME_TEAM4'] == name].values[0])
        elif name in list(master2['NAME_TEAM5']):
            players.append(master2[column2][master2['NAME_TEAM5'] == name].values[0])
        elif name in list(master2['NAME_TEAM6']):
            players.append(master2[column2][master2['NAME_TEAM6'] == name].values[0])
        else:
            players.append(df[column3][df[column] == name].values[0].upper())
    return players

pitchers_name3 = name_change2(pitchers, 'NAME_TEAM', 'NAME_TEAM', 'NAME_TEAM')
pitchers['NAME_TEAM'] = pitchers_name3
scores_weather3 = name_change2(scores_weather, 'NAME_TEAM_AWAY', 'NAME_TEAM', 'NAME_TEAM_AWAY')
scores_weather['NAME_TEAM_AWAY'] = scores_weather3
scores_weather2 = name_change2(scores_weather, 'NAME_TEAM_HOME', 'NAME_TEAM', 'NAME_TEAM_HOME')
scores_weather['NAME_TEAM_HOME'] = scores_weather2
scores_weather4 = name_change2(scores_weather, 'NAME_TEAM_HOME', 'PLAYERNAME', 'Starting_Pitcher_Home')
scores_weather['Starting_Pitcher_Home'] = scores_weather4
scores_weather5 = name_change2(scores_weather, 'NAME_TEAM_AWAY', 'PLAYERNAME', 'Starting_Pitcher_Away')
scores_weather['Starting_Pitcher_Away'] = scores_weather5

batters_name3 = name_change2(batters, 'NAME_TEAM', 'NAME_TEAM', 'NAME_TEAM')
batters['NAME_TEAM'] = batters_name3

for name in master2['PLAYERNAME']:
    try:
        if not master2['TEAM'][master2['PLAYERNAME'] == name].any() and master['TM'][master['mlb_name'] == name].any():
            master2['TEAM'][master2['PLAYERNAME'] == name] = master['TM'][master['mlb_name'] == name]
    except ValueError:
        if not master2['TEAM'][master2['PLAYERNAME'] == name].values[0] and master['TM'][master['mlb_name'] == name].any():
            master2['TEAM'][master2['PLAYERNAME'] == name] = master['TM'][master['mlb_name'] == name]
    else:
        master2['TEAM'][master2['PLAYERNAME'] == name] = None

teams = []
for name, team in zip(master2['PLAYERNAME'], master2['TEAM']):
    if not team:
        try:
            teams.append(master['TM'][master['mlb_name'] == name].values[0])
        except IndexError:
            teams.append(master['TM'][master['mlb_name'] == name].values)   
    else:
        teams.append(None)

teams = []
for name, team in zip(master2['PLAYERNAME'], master2['TEAM']):
    if not team:
        try:
            teams.append(master['TM'][master['mlb_name'] == name].values[0])
        except IndexError:
            teams.append(master['TM'][master['mlb_name'] == name].values)   
    else:
        teams.append(team)


master2['TEAM'] = teams
        
master2.to_csv('CSV/master3.csv', mode='w', index=False, header=True)
pitchers.to_csv('CSV/pitching_team1.csv', mode='w', index=False, header=True)
batters.to_csv('CSV/batter_team1.csv', mode='w', index=False, header=True)
scores_weather.to_csv('CSV/games_by_date1.csv', mode='w', index=False, header=True)
pitchers_rl.to_csv('CSV/pitcher_vs_rl.csv', mode='w', index=False, header=True)

