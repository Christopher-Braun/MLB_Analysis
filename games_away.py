import numpy as np
import pandas as pd
from constant_variables import PLAYER_TEAM
from constant_variables import PITCHERS_SIDE
from constant_variables import PLAYERS

master = pd.read_csv('CSV/master3.csv', encoding='latin-1')
scores_weather = pd.read_csv('CSV/games_by_date1.csv', encoding='latin-1')
batters = pd.read_csv('CSV/batter_team1.csv', encoding='latin-1')
pitchers = pd.read_csv('CSV/pitching_team1.csv', encoding='latin-1')
batters_left = pd.read_csv('CSV/batter_vs_left.csv', encoding='latin-1')
batters_right = pd.read_csv('CSV/batter_vs_right.csv', encoding='latin-1')
pitchers_vs_batterside = pd.read_csv('CSV/pitcher_vs_rl.csv', encoding='latin-1')
defensive_efficiency = pd.read_csv('CSV/defensive_effic.csv', encoding='latin-1')
team_offense  = pd.read_csv('CSV/team_off_adv.csv', encoding='latin-1')
bat_avg = pd.read_csv('CSV/batt_avg.csv', encoding='latin-1')
park_factor_hand = pd.read_csv('CSV/park_factor_hand.csv', encoding='latin-1')
bullpen = pd.read_csv('CSV/mlb_bullpen1.csv', encoding='latin-1')

def remove_first_column(df):
    # Remove first column of DataFrame
    return df.iloc[:, 1:]
    
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

def pitcher_hand(game):
    # Select whether to use batter stats against R or L handed pitchers
    if game[len(game)-1] == 'L':
        stat = batters_left
    else:
        stat = batters_right
    return stat

def add_player_info(df1, df2, col_new, col_name2, col_num1, col_num2):
    df2[col_new] = np.ones((len(df2[col_name2]),1))
    for df in df1.itertuples():
        df2[col_new] = df2[col_new].mask((df2[col_name2] == df[col_num1]), df[col_num2])
    return df2

# Check if player is in both dataframes
def player_check(frame1, frame2, frame1_name, frame2_name):
    frame1_not = []
    for player in list(frame1[frame1_name]):
        if player not in list(frame2[frame2_name]):
            frame1_not.append(player)
    return frame1_not

def switch_hitter_side(opp_pitcher, pl):
    # Find which side of the plate pitcher gets hit hardest by.  Set switch hitter to strongest side
    bat_right = pl['BASES_VS_AB_pit'][pl['HAND_pit'] == 'R'][pl['NAME'] == opp_pitcher['NAME'].values[0]]
    bat_left = pl['BASES_VS_AB_pit'][pl['HAND_pit'] == 'L'][pl['NAME'] == opp_pitcher['NAME'].values[0]]
    if pl['BASES_VS_AB_pit'][pl['HAND_pit'] == 'L'][pl['NAME'] == opp_pitcher['NAME'].values[0]].any() == False:
        bat_left = 0
    if pl['BASES_VS_AB_pit'][pl['HAND_pit'] == 'R'][pl['NAME'] == opp_pitcher['NAME'].values[0]].any() == False:
        bat_right = 0
    if float(bat_right) > float(bat_left):
        return 'R'
    else:
        return 'L'
 
def set_sides(lineup_sides):
    lineup = [switch_hitter_side(opp_pitcher, pitchers_vs_batterside) if i == 'B' else i for i in list(lineup_sides)]
    return lineup
  
def lineup_by_side_of_plate(sides, pl):
    # Compile pitcher stats against R/L hitters based on predicted num of each.  To be averaged later
    lineup = [pl[pl['HAND_pit'] == s][pl['NAME'] == opp_pitcher['NAME'].values[0]] for s in sides[:9]]
    lineup_side = pd.DataFrame(pd.concat([line for line in lineup]), columns = pl.columns)
    return lineup_side

def count_plate_side(sides):
    # Number of R/L in predicted lineup
    side_R = sides[:10].count('R')
    side_L = sides[:10].count('L')
    return [side_R, side_L]

def opp_pitch_ab(opp_pitcher, game):
    # Set away pitcher index and remove columns
    opp_pitcher = opp_pitcher.set_index(pd.Index([game[1]]))
    return opp_pitcher.iloc[:, 7:]
     
def stat_per_ab(bat_vs_pitcher_hand, game):
    # Average stats of top 10 batters in the lineup
    bat_vs_pitcher_hand = bat_vs_pitcher_hand.iloc[:10, 4:-2].mean()
    bat_vs_pitcher_hand = pd.DataFrame([bat_vs_pitcher_hand], index = pd.Index([game[4]]))
    return bat_vs_pitcher_hand
    
def per_ab(lineup_side_R, lineup_side_L, ab_R, ab_L): 
    # Divide by num of AB's
    lineup_side_R.iloc[:, 0:11] = round(lineup_side_R.iloc[:, 0:11].div(ab_R), 2)
    lineup_side_L.iloc[:, 0:11] = round(lineup_side_L.iloc[:, 0:11].div(ab_L), 2)
    return lineup_side_R, lineup_side_L

def ab_RL(lineup_side):
    if lineup_side['AB_SIDE_pit'][lineup_side['HAND_pit'] == 'R'].any() == False:
        ab_R = 1
    else:
        ab_R = lineup_side['AB_SIDE_pit'][lineup_side['HAND_pit'] == 'R'].values[0]
    if lineup_side['AB_SIDE_pit'][lineup_side['HAND_pit'] == 'L'].any() == False:
        ab_L = 1
    else:
        ab_L = lineup_side['AB_SIDE_pit'][lineup_side['HAND_pit'] == 'L'].values[0]
    return ab_R, ab_L

def lineup_park_factor(lineup_side, park_factor):
    # Combine Pitcher stats vs R & L batters.  Avg stats based on probable lineup (num of R/L). Add Park Factor
    ab_R, ab_L = ab_RL(lineup_side)
    park_factor_R = park_factor.iloc[:, 7:][park_factor['SIDE'] == 'RHB']
    park_factor_L = park_factor.iloc[:, 7:][park_factor['SIDE'] == 'LHB']
    lineup_side_R = lineup_side.iloc[:, 6:][lineup_side['HAND_pit'] == 'R']
    lineup_side_L = lineup_side.iloc[:, 6:][lineup_side['HAND_pit'] == 'L']
    lineup_side_R, lineup_side_L = per_ab(lineup_side_R, lineup_side_L, ab_R, ab_L)
    lineup_side_R.iloc[:,[0,1,2,3,11,12,13,14,19,20]] = round(lineup_side_R.iloc[:,[0,1,2,3,11,12,13,14,19,20]]*park_factor_R.iloc[:, [4,5,6,7,0,1,2,3,7,8]].values[0],3)
    lineup_side_L.iloc[:,[0,1,2,3,11,12,13,14,19,20]] = round(lineup_side_L.iloc[:,[0,1,2,3,11,12,13,14,19,20]]*park_factor_L.iloc[:, [4,5,6,7,0,1,2,3,7,8]].values[0],3)
    return lineup_side_R, lineup_side_L
    
def lineup_park_avg(lineup_side_R, lineup_side_L):
    # Avg pitcher stats based on park and num of R/L handed batters in lineup
    lineup_park_avg = (lineup_side_R.sum() + lineup_side_L.sum())/(len(lineup_side_R) + len(lineup_side_L))
    lineup_park_avg = round(lineup_park_avg,3)
    return lineup_park_avg

# Drop rows
batters, batters_left, batters_right = remove_first_column(batters), remove_first_column(batters_left), remove_first_column(batters_right)
pitchers, pitchers_vs_batterside = remove_first_column(pitchers), remove_first_column(pitchers_vs_batterside)
park_factor_hand, defensive_efficiency = remove_first_column(park_factor_hand), remove_first_column(defensive_efficiency)

# Change names to match master sheet
pitchers_vs_batterside['NAME'] = list(map((lambda x:get_player_name(x)), pitchers_vs_batterside['NAME'].values))
pitchers_vs_batterside[['FB%_SIDE_pit', 'GB%_SIDE_pit', 'LD%_SIDE_pit', 'POP%_SIDE_pit']] = round(pitchers_vs_batterside[['FB%_SIDE_pit', 'GB%_SIDE_pit', 'LD%_SIDE_pit', 'POP%_SIDE_pit']]/100, 3)

# Change team ini's and pitcher names to type category
scores_weather['Away'] = scores_weather['Away'].astype('category')
scores_weather['Home'] = scores_weather['Home'].astype('category')
scores_weather['Starting_Pitcher_Away'] = scores_weather['Starting_Pitcher_Away'].astype('category')
scores_weather['Starting_Pitcher_Home'] = scores_weather['Starting_Pitcher_Home'].astype('category')

# Change master player teams to be current
for k,v in PLAYER_TEAM.items():
    master['TEAM'] = master['TEAM'].mask((master['PLAYERNAME'] == k), v)
    master['NAME_TEAM'] = master['NAME_TEAM'].mask((master['PLAYERNAME'] == k), k + ' ' + v)
    
# Add column
master['NAME_TEAM'] = master['PLAYERNAME'] + ' ' + master['TEAM']

# Change columns to type category
master['PLAYERNAME'] = master['PLAYERNAME'].astype('category')
master['TEAM'] = master['TEAM'].astype('category')
master['THROWS'] = master['THROWS'].astype('category')
master['BATS'] = master['BATS'].astype('category')

# Combine batters with pitcher info
batter_template1 = pd.merge(master, batters, on='NAME_TEAM', how='inner')
batters_not1 = player_check(batters, batter_template1, 'NAME', 'PLAYERNAME')
pitcher_template1 = pd.merge(master, pitchers, on='NAME_TEAM', how='inner')
pitchers_not1 = player_check(pitchers, pitcher_template1, 'NAME', 'PLAYERNAME')

# Add home pitcher's throwing hand
master = master.rename(columns={'PLAYERNAME' : 'Starting_Pitcher_Home', 'TEAM' : 'Home', 'THROWS' : 'Home_Arm'})
scores_weather['Home_Arm'] = np.ones((len(scores_weather),1))
for i,row in enumerate(scores_weather.iterrows()):
    mask = (master['Starting_Pitcher_Home'] == row[1][18]) & (master['Home'] == row[1][3])
    if len(master[mask]) > 0:
        scores_weather['Home_Arm'][i] = master[mask]['Home_Arm'].values[0]

# Add away pitcher's throwing hand
master = master.rename(columns={'Starting_Pitcher_Home' : 'Starting_Pitcher_Away', 'Home' : 'Away', 'Home_Arm' : 'Away_Arm'})
scores_weather['Away_Arm'] = np.ones((len(scores_weather),1))
for i,row in enumerate(scores_weather.iterrows()):
    mask = (master['Starting_Pitcher_Away'] == row[1][15]) & (master['Away'] == row[1][0])
    if len(master[mask]) > 0:
        scores_weather['Away_Arm'][i] = master[mask]['Away_Arm'].values[0]

# Add batter's strong hand
batters['HAND'] = np.ones((len(batters['NAME']),1))
for player in master.itertuples():
    mask = (batters['NAME'] + ' ' + batters['TEAM'] == player[43])
    batters['HAND'] = batters['HAND'].mask(mask, player[27])

# Change columns to type category
batters['TEAM'] = batters['TEAM'].astype('category')
batters['NAME'] = batters['NAME'].astype('category')
batters['HAND'] = batters['HAND'].astype('category')

# Add team initials
batters_left = add_player_info(batters, batters_left, 'TEAM', 'NAME', 1, 2)
batters_right = add_player_info(batters, batters_right, 'TEAM', 'NAME', 1, 2)

# Add batter's strong hand
batters_left = add_player_info(batters, batters_left, 'HAND', 'NAME', 1, len(batters.columns))
batters_right = add_player_info(batters, batters_right, 'HAND', 'NAME', 1, len(batters.columns))

# Change column name
pitchers_vs_batterside = pitchers_vs_batterside.set_axis(PITCHERS_SIDE, axis = 'columns', inplace=False)

# Fill batting hand for players that switched teams num [ugly and inefficient]
unknown = batters[batters['HAND'] == 1]['NAME']
hand_missing = set()
batters1 = batters

# Change columns to type category
batters_left['TEAM'] = batters_left['TEAM'].astype('category')
batters_left['NAME'] = batters_left['NAME'].astype('category')
batters_left['HAND'] = batters_left['HAND'].astype('category')

batters_right['TEAM'] = batters_right['TEAM'].astype('category')
batters_right['NAME'] = batters_right['NAME'].astype('category')
batters_right['HAND'] = batters_right['HAND'].astype('category')

pitchers['TEAM'] = pitchers['TEAM'].astype('category')
pitchers['NAME'] = pitchers['NAME'].astype('category')

pitchers_vs_batterside['NAME'] = pitchers_vs_batterside['NAME'].astype('category')
pitchers_vs_batterside['HAND_pit'] = pitchers_vs_batterside['HAND_pit'].astype('category')

dup = master[master['IDPLAYER'] == 'perdolu01'].index[0]
master = master.drop([dup])

# Player batting/throwing hand by comparing player name and team.  Non-matches(traded players) are filled in by name alone.
for name in unknown:
    mask = (len(master['Starting_Pitcher_Away'][master['Starting_Pitcher_Away'] == name]) > 1) & (batters['HAND'][batters['NAME'] == name] == 1)
    try:
        batters['HAND'][batters['NAME'] == name] = master['BATS'][master['Starting_Pitcher_Away'].mask(mask).notna()].values[0]
    except IndexError:
        print(name + "'s batting side is not in the database" )
        hand_missing.add(name)

unknown = scores_weather[scores_weather['Away_Arm'] == 1]['Starting_Pitcher_Away']
for name in unknown:
    mask = (len(master['Starting_Pitcher_Away'][master['Starting_Pitcher_Away'] == name]) > 1) & (scores_weather['Away_Arm'][scores_weather['Starting_Pitcher_Away'] == name] == 1)
    try:
        scores_weather['Away_Arm'][scores_weather['Starting_Pitcher_Away'] == name] = master['Away_Arm'][master['Starting_Pitcher_Away'].mask(mask).notna()].values[0]
    except IndexError:
        print(name + "'s pitching arm is not in the database" )
        hand_missing.add(name)
        
unknown = scores_weather[scores_weather['Home_Arm'] == 1]['Starting_Pitcher_Home']
for name in unknown:
    mask = (len(master['Starting_Pitcher_Away'][master['Starting_Pitcher_Away'] == name]) > 1) & (scores_weather['Home_Arm'][scores_weather['Starting_Pitcher_Home'] == name] == 1)
    try:
        scores_weather['Home_Arm'][scores_weather['Starting_Pitcher_Home'] == name] = master['Away_Arm'][master['Starting_Pitcher_Away'].mask(mask).notna()].values[0]
    except IndexError:
        print(name + "'s pitching arm is not in the database" )
        hand_missing.add(name)

unknown = scores_weather[scores_weather['Home_Arm'] == 1]['Starting_Pitcher_Home']
for name in unknown:
    if scores_weather['Home_Arm'][scores_weather['Starting_Pitcher_Home'] == name].values[0] == 1:
        scores_weather['Home_Arm'][scores_weather['Starting_Pitcher_Home'] == name] = master['Away_Arm'][master['Starting_Pitcher_Away'] == name]

unknown = scores_weather[scores_weather['Away_Arm'] == 1]['Starting_Pitcher_Away']
for name in unknown:
    if scores_weather['Away_Arm'][scores_weather['Starting_Pitcher_Away'] == name].values[0] == 1:
        scores_weather['Away_Arm'][scores_weather['Starting_Pitcher_Away'] == name] = master['Away_Arm'][master['Starting_Pitcher_Away'] == name]

batters['HAND'][batters['NAME'] == 'CHRIS YOUNG'] = 'R'

# Set index and divide categories by AB's or IP's
team_offense = team_offense.set_index(team_offense.iloc[:,0])
team_offense = team_offense.iloc[:,2:]

defensive_efficiency = defensive_efficiency.set_index(defensive_efficiency.TEAM.values)
defensive_efficiency.iloc[:, 3:7] = round(defensive_efficiency.iloc[:, 3:7].div(defensive_efficiency.PA_Def_Ef, axis = 0), 2)
defensive_efficiency = defensive_efficiency.iloc[:, 3:]

pitchers = pitchers.drop(columns = ['NAME_TEAM'])
pitchers.iloc[:, 7:17] = round(pitchers.iloc[:, 7:17].div(pitchers.IP_Pitching_Std, axis = 0), 3)
pitchers.iloc[:, 7:19] = round(pitchers.iloc[:, 7:19].mul((pitchers.IP_Pitching_Std/pitchers.G_Pitching_Std)/9, axis = 0), 3)
pitchers.iloc[:, [20,22,23]] = round(pitchers.iloc[:, [20,22,23]].mul(((9-pitchers.IP_Pitching_Std/pitchers.G_Pitching_Std))/9, axis = 0), 3)
pitchers['BASES_VS_AB_Pitching_Std'] = round(pitchers.BASES_VS_AB_Pitching_Std.mul((pitchers.IP_Pitching_Std/pitchers.G_Pitching_Std)/9, axis = 0), 3)

batters = batters.drop(columns = ['NAME_TEAM'])
batters.iloc[:, 5:17] = round(batters.iloc[:, 5:17].div(batters.PA, axis = 0), 3)

batters_left = batters_left.sort_values(by = batters_left.columns[2], ascending = False)
batters_left.iloc[:, 4:18] = round(batters_left.iloc[:, 4:18].div(batters_left.PA_LEFT_batter_Std, axis = 0), 3)
batters_right = batters_right.sort_values(by = batters_right.columns[2], ascending = False)
batters_right.iloc[:, 4:18] = round(batters_right.iloc[:, 4:18].div(batters_right.PA_RIGHTbatter_Std, axis = 0), 3)

# Rounding off high decimal columns
pitchers['BASES_VS_AB_Pitching_Std'] = round(pitchers['BASES_VS_AB_Pitching_Std'], 2)
pitchers_vs_batterside['BASES_VS_AB_pit'] = round(pitchers_vs_batterside['BASES_VS_AB_pit'], 2)
batters['BASES_VS_AB'] = round(batters['BASES_VS_AB'], 2)
batters_right['BASES_VS_AB_RIGHTbatter_Std'] = round(batters_right['BASES_VS_AB_RIGHTbatter_Std'], 2)
batters_left['BASES_VS_AB_LEFT_batter_Std'] = round(batters_left['BASES_VS_AB_LEFT_batter_Std'], 2)

# Change columns to type category
scores_weather['Direction'] = scores_weather['Direction'].astype('category')
scores_weather['Location'] = scores_weather['Location'].astype('category')
scores_weather['Time'] = scores_weather['Time'].astype('category')

scores_weather['Away_Arm'][scores_weather['Starting_Pitcher_Away'] == 'A.J. COLE'] = 'R'
scores_weather['Home_Arm'][scores_weather['Starting_Pitcher_Home'] == 'A.J. COLE'] = 'R'

bullpen = bullpen.set_index(bullpen['TEAM_INI'])
bullpen = bullpen.iloc[:, 1:]
bullpen_cols = [str(i) + '_bul' for i in bullpen.columns]
bullpen.columns = bullpen_cols

game_comp, pitcher_NA = [], []
# Compile all individual game stats
for game in scores_weather.itertuples():
    if game[16] in list(pitchers['NAME']) and game[16] in list(pitchers_vs_batterside['NAME']):
        team_bat = pd.DataFrame([team_offense.loc[game[4]]],  index = pd.Index([game[4]]), columns = team_offense.columns)  # Home Team
        team_def = pd.DataFrame([defensive_efficiency.loc[game[1]]], index = pd.Index([game[1]]), columns = defensive_efficiency.columns)  # Away Team        
        opp_pitcher = pitchers[pitchers['TEAM'] == game[1]][pitchers['NAME'] == game[16]]  # Away Team
        bat_vs_pitcher_hand = pitcher_hand(game)[pitcher_hand(game)['TEAM'] ==  game[4]]  # Home Team
        park_factor = park_factor_hand[park_factor_hand['TEAM'] == game[4]]  # Home Stadium
        bullpen1 = pd.DataFrame([bullpen.loc[game[1]].values], index = pd.Index([game[1]]), columns = bullpen.columns)  # Away Team        
        bullpen1.iloc[:,[0,10]] = round(bullpen1.iloc[:,[0,10]].mul(((9-(opp_pitcher.IP_Pitching_Std/opp_pitcher.G_Pitching_Std))/9).values[0]), 3)
        bullpen1.iloc[:,[1,2,3,6,7,8,9]] = round(bullpen1.iloc[:,[1,2,3,6,7,8,9]].mul(((opp_pitcher.IP_Pitching_Std/opp_pitcher.G_Pitching_Std)/9).values[0]), 3)

        # Create teams top lineup [Switch hitters pick best side based on pitcher arm]
        bat_team = batters[batters['TEAM'] == game[4]].sort_values(by = ['PA'], ascending = False)  # Home Team
        bat_vs_pitcher_hand = bat_vs_pitcher_hand.sort_values(by = bat_vs_pitcher_hand.columns[2], ascending = False)
        bat_pitcher_hand = stat_per_ab(bat_vs_pitcher_hand, game)

        # Predict lineup and average stats
        sides = set_sides(bat_team.iloc[:11, -1])
        lineup_side = lineup_by_side_of_plate(sides, pitchers_vs_batterside)
        lineup_side_R, lineup_side_L = lineup_park_factor(lineup_side, park_factor)
        lineup_side_mean = lineup_park_avg(lineup_side_R, lineup_side_L)
        lineup_side_mean = lineup_side_mean.rename(game[1]) # Away Team
        lineup_side_means = pd.DataFrame([lineup_side_mean], index = [lineup_side_mean.name], columns = lineup_side_mean.index)

        # Set away pitcher index and remove columns
        opp_pitcher = opp_pitch_ab(opp_pitcher, game)

        # Merge offensive and defensive stats
        away_merge = lineup_side_means.join([opp_pitcher, team_def, bullpen1])
        home_merge = team_bat.join([bat_pitcher_hand])
        home_merge = home_merge.set_index(pd.Index([game[1]]))
        home_away = away_merge.join(home_merge)
        game_ind = (game[22] + ' ' + home_away.index[0] + ' ' + game[4])
        home_away = home_away.set_index(pd.Index([game_ind]))
        weather = pd.DataFrame([[game[5], game[6], game[7], game[9], game[10], game[11], game[12], game[13]]], columns = ['Proj_Runs', 'Runs', 'Time', 'Temp', 'Humidity', 'Wind', 'Direction', 'Location'])
        home_away_score = home_away.join(weather.set_index(pd.Index([game_ind])))

        # Combine all single game stats
        game_comp.append(home_away_score)
        print(game[22])
    else:
        pitcher_NA.append(game[16])
        print(game)

games1 = np.vstack([game for game in game_comp])
games = pd.DataFrame(np.vstack([game for game in game_comp]), index = np.hstack([game.index for game in game_comp]), columns = game_comp[0].columns)
df_cols = [i.replace('RIGHT', 'SIDE') for i in list(games.columns)]
df_cols1 = [i.replace('LEFT_', 'SIDE') for i in df_cols]

games2 = pd.concat([pd.DataFrame(game.values, index = game.index, columns = df_cols1) for game in game_comp], ignore_index = False)
games2.to_csv('CSV/game_away3.csv', mode='w', index=True, header=True)

