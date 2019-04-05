import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import scipy.stats as stats
import matplotlib.pyplot as plt

# Import Home and Away Games, Add Stadium Column
games_away = pd.read_csv('MLB/game_away3.csv', encoding='latin-1', index_col = False)
games_home = pd.read_csv('MLB/game_home3.csv', encoding='latin-1', index_col = False)

games_away['Direction'][games_away['Direction'] == 'None'] = '0'
games_away['Direction'][games_away['Direction'].isna()] = '0'
games_home['Direction'][games_home['Direction'] == 'None'] = '0'
games_home['Direction'][games_home['Direction'].isna()] = '0'

games_away['Location'][games_away['Location'] == 'None'] = '0'
games_away['Location'][games_away['Location'].isna()] = '0'
games_home['Location'][games_home['Location'] == 'None'] = '0'
games_home['Location'][games_home['Location'].isna()] = '0'

runs_away = games_away['Runs']
runs_home = games_home['Runs']

runs_away_proj = games_away['Proj_Runs']
runs_home_proj = games_home['Proj_Runs']

games_away = games_away.drop(columns = ['Runs'])
games_home = games_home.drop(columns = ['Runs'])

games_away = games_away.drop(columns = ['Proj_Runs'])
games_home = games_home.drop(columns = ['Proj_Runs'])

teams_off = pd.Series([i[-3:] for i in games_away.iloc[:,0]])
teams1_off = pd.Series([i[-3:] for i in games_home.iloc[:,0]])

teams_def = pd.Series([i[-7:-4] for i in games_away.iloc[:,0]])
teams1_def = pd.Series([i[-7:-4] for i in games_home.iloc[:,0]])

games_away['STADIUM'] = teams_off
games_home['STADIUM'] = teams1_def

# Combine Home and Away Games
games = pd.concat([games_away, games_home])
runs = pd.concat([runs_away, runs_home])
runs_proj = pd.concat([runs_away_proj, runs_home_proj])
games['Runs'] = runs
games['Proj_Runs'] = runs_proj

# Make Wind MPH Negative if it's Blowing In
games['Direction'] = [i if (i == 'out' or i == 'in') else '0' for i in games['Direction']]
games['Location'] = [i if (i == 'LF' or i == 'CF' or i == 'RF') else '0' for i in games['Location']]
games['Wind'] = [i*(-1) if j == 'in' else i for i,j in zip(games['Wind'], games['Direction'])]
games['Wind'] = [0 if j == '0' else i for i,j in zip(games['Wind'], games['Direction'])]

# Create Wind Level Categorys [In, None, Out]
games['Wind_Level'] = games['Wind'].apply(lambda value: 'low' 
                                                  if int(value) < 0 else 'medium' 
                                                      if int(value) == 0 else 'high')

games.loc[:,('Wind_Level')] = pd.Categorical(games.loc[:,('Wind_Level')], 
                                           categories=['low', 'medium', 'high'])

games['Wind_Level'] = games['Wind_Level'].apply(lambda value: 1 
                                             if value == 'low' else 2
                                                 if value == 'medium' else 3)

games['STADIUM'] = games['STADIUM'].astype('category')

# Average Runs and Standard Deviations under each Wind Condition in Specified Stadium
def wind_mean(team, wind_level):
    return np.round(np.mean(games['Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team)]),2)

def wind_var(team, wind_level):
    return np.round(np.std(games['Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team)]),2)

def wind_mean_proj(team, wind_level):
    return np.round(np.mean(games['Proj_Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team)]),2)

def wind_var_proj(team, wind_level):
    return np.round(np.std(games['Proj_Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team)]),2)

# List of all Teams
teams = list(games['STADIUM'].unique())

# Sort Teams by difference in Avg Proj Runs between Wind blowing out and in
bars1 = [wind_mean(team, 3) for team in teams]
bars2 = [wind_mean(team, 1) for team in teams]

def sort_teams(bars1, bars2, teams):
    bars1 = [0 if str(i) == 'nan' else i for i in bars1]
    bars2 = [0 if str(i) == 'nan' else i for i in bars2]
    bars_dif = [np.round(i-j,2) for i,j in zip(bars1, bars2)]
    df = pd.DataFrame(np.column_stack((teams, bars_dif)), columns = ['Teams', 'Bars'])
    df1 = df.sort_values(by = 'Bars')
    return df1.Teams.values

# Are there more runs scored when the wind is blowing out?

# Plot Avg Runs Scored with the Wind Blowing In and Out at each Stadium
barWidth = 0.35

bars1 = [wind_mean(team, 3) for team in teams]
bars2 = [wind_mean(team, 1) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean(team, 3) for team in team_sort]
bars2 = [wind_mean(team, 1) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out vs Wind In", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Runs Scored with the Wind Blowing In, Out and Not Blowing at each Stadium

# set width of bar
barWidth = 0.25
 
# set height of bar
bars1 = [wind_mean(team, 3) for team in team_sort]
bars2 = [wind_mean(team, 2) for team in team_sort]
bars3 = [wind_mean(team, 1) for team in team_sort]
 
# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
#title = fig.suptitle("Wind Out - No Wind - Wind In", fontsize=14)
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out')
ax.bar(r2, bars2, color='MediumOrchid', width=barWidth, edgecolor='white', label='No Wind')
ax.bar(r3, bars3, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In')
 
# Add xticks on the middle of the group bars
plt.xlabel('group', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Wind Out - No Wind - Wind In", fontsize=14)
plt.legend()
plt.show()

# Does pitcher fly ball percentage impact the wind effect?

# Create column for pitchers with High, Low and Avg Fly Ball Percentages
ma = max(games['FB%_SIDE_pit'])
mi = min(games['FB%_SIDE_pit'])
m3 = (ma-mi)/3

games['FB%_Level'] = games['FB%_SIDE_pit'].apply(lambda value: 'low' 
                                                  if value < (mi+m3) else 'medium' 
                                                      if value == (ma-m3) else 'high')

games.loc[:,('FB%_Level')] = pd.Categorical(games.loc[:,('FB%_Level')], 
                                           categories=['low', 'medium', 'high'])

games['FB%_Level'] = games['FB%_Level'].apply(lambda value: 1 
                                             if value == 'low' else 2
                                                 if value == 'medium' else 3)

# Average Proj Runs with High and Low MPH Wind Conditions under all Fly Ball % categories in the Specified Stadium
def wind_mean_fb(team, wind_level, fb_percent_level):
    return np.round(np.mean(games['Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team) & (games['FB%_Level'] == fb_percent_level)]),2)

def wind_mean_fb_proj(team, wind_level, fb_percent_level):
    return np.round(np.mean(games['Proj_Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team) & (games['FB%_Level'] == fb_percent_level)]),2)

# Plot Avg Runs Scored with the Wind Blowing In and Out for High FB% pitchers at each Stadium
barWidth = 0.35

bars1 = [wind_mean_fb(team, 3, 3) for team in teams]
bars2 = [wind_mean_fb(team, 1, 3) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_fb(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb(team, 1, 3) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out_High_FB%')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In_High_FB%')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out - High FB% vs Wind In - High FB%", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Runs Scored with the Wind Blowing Out for High FB% pitchers at each Stadium
barWidth = 0.35
 
bars1 = [wind_mean_fb(team, 3, 3) for team in teams]
bars2 = [wind_mean_fb(team, 3, 1) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_fb(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb(team, 3, 1) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out_High_FB%')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind Out_Low_FB%')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out - High FB% vs Wind Out - Low FB%", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Runs Scored with the Wind Blowing In, Out and Not Blowing at each Stadium

# set width of bar
barWidth = 0.25
 
# set height of bar
bars1 = [wind_mean_fb(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb(team, 3, 2) for team in team_sort]
bars3 = [wind_mean_fb(team, 3, 1) for team in team_sort]
 
# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out')
ax.bar(r2, bars2, color='MediumOrchid', width=barWidth, edgecolor='white', label='No Wind')
ax.bar(r3, bars3, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In')
 
# Add xticks on the middle of the group bars
plt.xlabel('group', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.legend()
plt.show()

# Determine how much projected runs are effected by wind speeds

# Plot Avg Proj Runs Scored with the Wind Blowing In and Out at each Stadium
barWidth = 0.35

bars1 = [wind_mean_proj(team, 3) for team in teams]
bars2 = [wind_mean_proj(team, 1) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_proj(team, 3) for team in team_sort]
bars2 = [wind_mean_proj(team, 1) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]

# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Proj Runs: Wind Out vs Wind In", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Proj Runs Scored with the Wind Blowing In, Out and Not Blowing at each Stadium

# set width of bar
barWidth = 0.25
 
# set height of bar
bars1 = [wind_mean_proj(team, 3) for team in team_sort]
bars2 = [wind_mean_proj(team, 2) for team in team_sort]
bars3 = [wind_mean_proj(team, 1) for team in team_sort]
 
# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='No Wind')
ax.bar(r3, bars3, color='MediumOrchid', width=barWidth, edgecolor='white', label='Wind In')
 
# Add xticks on the middle of the group bars
plt.xlabel('group', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Proj Runs: Wind Out - No Wind - Wind In", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Proj Runs Scored with the Wind Blowing In and Out for High FB% pitchers at each Stadium
barWidth = 0.35
 
bars1 = [wind_mean_fb_proj(team, 3, 3) for team in teams]
bars2 = [wind_mean_fb_proj(team, 1, 3) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_fb_proj(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb_proj(team, 1, 3) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out_High_FB%')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In_High_FB%')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Proj Runs: Wind Out - High FB% vs Wind In - High FB%", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Proj Runs Scored with the Wind Blowing Out for High FB% pitchers at each Stadium
barWidth = 0.35
 
bars1 = [wind_mean_fb_proj(team, 3, 3) for team in teams]
bars2 = [wind_mean_fb_proj(team, 3, 1) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_fb_proj(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb_proj(team, 3, 1) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out_High_FB%')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind Out_Low_FB%')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Proj Runs: Wind Out - High FB% vs Wind Out - Low FB%", fontsize=14)
plt.legend()
plt.show()

# Only count wind speeds larger than 4 MPH

# Create Wind Level Categorys [In, None, Out]
games['Wind_Level'] = games['Wind'].apply(lambda value: 'low' 
                                                  if int(value) < -4 else 'medium' 
                                                      if int(value) < 4 else 'high')

games.loc[:,('Wind_Level')] = pd.Categorical(games.loc[:,('Wind_Level')], 
                                           categories=['low', 'medium', 'high'])

games['Wind_Level'] = games['Wind_Level'].apply(lambda value: 1 
                                             if value == 'low' else 2
                                                 if value == 'medium' else 3)

# Plot Avg Runs Scored with the Wind Blowing In and Out at each Stadium
barWidth = 0.35

bars1 = [wind_mean(team, 3) for team in teams]
bars2 = [wind_mean(team, 1) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean(team, 3) for team in team_sort]
bars2 = [wind_mean(team, 1) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out vs Wind In", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Runs Scored with the Wind Blowing In and Out for High FB% pitchers at each Stadium
barWidth = 0.35

bars1 = [wind_mean_fb(team, 3, 3) for team in teams]
bars2 = [wind_mean_fb(team, 1, 3) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_fb(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb(team, 1, 3) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out_High_FB%')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In_High_FB%')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out - High FB% vs Wind In - High FB%", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Runs Scored with the Wind Blowing Out for High FB% pitchers at each Stadium
barWidth = 0.35
 
bars1 = [wind_mean_fb(team, 3, 3) for team in teams]
bars2 = [wind_mean_fb(team, 3, 1) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_fb(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb(team, 3, 1) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out_High_FB%')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind Out_Low_FB%')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out - High FB% vs Wind Out - Low FB%", fontsize=14)
plt.legend()
plt.show()

# Only count wind speeds above 5 MPH

# Create Wind Level Categorys [In - Minimal, High]
games['Wind_Level'] = games['Wind'].apply(lambda value: 'low'  
                                                  if int(value) < 5 else 'high')

games.loc[:,('Wind_Level')] = pd.Categorical(games.loc[:,('Wind_Level')], 
                                           categories=['low', 'high'])

games['Wind_Level'] = games['Wind_Level'].apply(lambda value: 1 
                                                 if value == 'low' else 3)

# Plot Avg Runs Scored with the Wind Blowing In and Out at each Stadium
barWidth = 0.35

bars1 = [wind_mean(team, 3) for team in teams]
bars2 = [wind_mean(team, 1) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean(team, 3) for team in team_sort]
bars2 = [wind_mean(team, 1) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out vs Wind In", fontsize=14)
plt.legend()
plt.show()

min(games['Wind'])

# Plot Avg Runs Scored with the Wind Blowing In and Out for High FB% pitchers at each Stadium
barWidth = 0.35

bars1 = [wind_mean_fb(team, 3, 3) for team in teams]
bars2 = [wind_mean_fb(team, 1, 3) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_fb(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb(team, 1, 3) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out_High_FB%')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind In_High_FB%')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out - High FB% vs Wind In - High FB%", fontsize=14)
plt.legend()
plt.show()

# Plot Avg Runs Scored with the Wind Blowing Out for High FB% pitchers at each Stadium
barWidth = 0.35
 
bars1 = [wind_mean_fb(team, 3, 3) for team in teams]
bars2 = [wind_mean_fb(team, 3, 1) for team in teams]
team_sort = sort_teams(bars1, bars2, teams)
 
# set height of bar
bars1 = [wind_mean_fb(team, 3, 3) for team in team_sort]
bars2 = [wind_mean_fb(team, 3, 1) for team in team_sort]

# Set position of bar on X axis
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
 
# Make the plot
fig = plt.figure(figsize=(20, 10))
ax = fig.subplots()
ax.bar(r1, bars1, color='SkyBlue', width=barWidth, edgecolor='white', label='Wind Out_High_FB%')
ax.bar(r2, bars2, color='IndianRed', width=barWidth, edgecolor='white', label='Wind Out_Low_FB%')
 
# Add xticks on the middle of the group bars
plt.xlabel('Stadiums', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(bars1))], team_sort)
 
# Create legend & Show graphic
plt.title("Avg Runs: Wind Out - High FB% vs Wind Out - Low FB%", fontsize=14)
plt.legend()
plt.show()

# Plot to examine distribution of runs scored
from scipy.stats import norm
sns.distplot(runs)

team_dict, teams_dict = dict(), dict()

# Runs under each Wind Condition in Specified Stadium
def wind_runs(team, wind_level):
    return games['Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team)]

def wind_runs_proj(team, wind_level):
    return games['Proj_Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team)]

# Runs with High and Low MPH Wind Conditions under all Fly Ball % categories in the Specified Stadium
def wind_fb(team, wind_level, fb_percent_level):
    return games['Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team) & (games['FB%_Level'] == fb_percent_level)]

def wind_fb_proj(team, wind_level, fb_percent_level):
    return games['Proj_Runs'][(games['Wind_Level'] == wind_level) & (games['STADIUM'] == team) & (games['FB%_Level'] == fb_percent_level)]

#sns.regplot(wind_team, runs_team)

for team in teams:
    runs_team = games['Runs'][games['STADIUM'] == team]
    wind_team = games['Wind'][games['STADIUM'] == team]
    runs_high = wind_runs(team, 3)
    runs_medium = wind_runs(team, 2)
    runs_low = wind_runs(team, 1)
    runs_high_proj = wind_runs_proj(team, 3)
    runs_medium_proj = wind_runs_proj(team, 2)
    runs_low_proj = wind_runs_proj(team, 1)
    runs_high_wind_fb = wind_fb(team, 3, 3)
    runs_medium_wind_fb = wind_fb(team, 2, 3)
    runs_low_wind_fb = wind_fb(team, 1, 3)
    runs_high_wind_fb_proj = wind_fb_proj(team, 3, 3)
    runs_medium_wind_fb_proj = wind_fb_proj(team, 2, 3)
    runs_low_wind_fb_proj = wind_fb_proj(team, 1, 3)
    runs_high_fb = wind_fb(team, 3, 3)
    runs_medium_fb = wind_fb(team, 3, 2)
    runs_low_fb = wind_fb(team, 3, 1)
    runs_high_fb_proj = wind_fb_proj(team, 3, 3)
    runs_medium_fb_proj = wind_fb_proj(team, 3, 2)
    runs_low_fb_proj = wind_fb_proj(team, 3, 1)
    shapiro_runs = stats.shapiro(runs_team)
    
    if runs_high.any() & runs_medium.any() & runs_low.any():
        wilcoxon = stats.ranksums(runs_high, runs_team)
        mannwhit = stats.mannwhitneyu(runs_high, runs_low)
        kruskal = stats.kruskal(runs_high, runs_medium, runs_low)
    elif runs_high.any() & runs_low.any():
        wilcoxon = stats.ranksums(runs_high, runs_team)
        mannwhit = stats.mannwhitneyu(runs_high, runs_low)
        kruskal = (0, 0)
    elif runs_high.any():
        wilcoxon = stats.ranksums(runs_high, runs_team)
        mannwhit = (0, 0)
        kruskal = (0, 0)
    else:
        wilcoxon = (0, 0)
        mannwhit = (0, 0)
        kruskal = (0, 0)
        
    if runs_high_wind_fb.any() & runs_low_wind_fb.any() & runs_medium_wind_fb.any():
        wilcoxon1 = stats.ranksums(runs_high_wind_fb, runs_team)
        kruskal1 = stats.kruskal(runs_high_wind_fb, runs_medium_wind_fb, runs_low_wind_fb)
        mannwhit1 = stats.mannwhitneyu(runs_high_wind_fb, runs_low_wind_fb)
    elif runs_high_wind_fb.any() & runs_low_wind_fb.any():
        wilcoxon1 = stats.ranksums(runs_high_wind_fb, runs_team)
        kruskal1 = (0, 0)
        mannwhit1 = stats.mannwhitneyu(runs_high_wind_fb, runs_low_wind_fb)
    elif runs_high_wind_fb.any():
        wilcoxon1 = stats.ranksums(runs_high_wind_fb, runs_team)
        kruskal1 = (0, 0)
        mannwhit1 = (0, 0)
    else:
        wilcoxon1 = (0, 0)
        kruskal1 = (0, 0)
        mannwhit1 = (0, 0)
        
    if runs_high_fb.any() & runs_low_fb.any() & runs_medium_fb.any():
        wilcoxon2 = stats.ranksums(runs_high_fb, runs_team)
        kruskal2 = stats.kruskal(runs_high_fb, runs_medium_fb, runs_low_fb)
        mannwhit2 = stats.mannwhitneyu(runs_high_fb, runs_low_fb)
    elif runs_high_fb.any() & runs_low_fb.any():
        wilcoxon2 = stats.ranksums(runs_high_fb, runs_team)
        kruskal2 = (0, 0)
        mannwhit2 = stats.mannwhitneyu(runs_high_fb, runs_low_fb)
    elif runs_high_fb.any():
        wilcoxon2 = stats.ranksums(runs_high_fb, runs_team)
        kruskal2 = (0, 0)
        mannwhit2 = (0, 0)
    else:
        wilcoxon2 = (0, 0)
        kruskal2 = (0, 0)
        mannwhit2 = (0, 0)
    
    team_dict = {'Normality' : np.round(shapiro_runs[1],3), 'Wilcoxon' : [np.round(wilcoxon[1],3), np.round(wilcoxon1[1],3), np.round(wilcoxon2[1],3)], 'Kruskal' : [np.round(kruskal[1],3), np.round(kruskal1[1],3), np.round(kruskal2[1],3)], 'Mannwhit' : [np.round(mannwhit[1],3), np.round(mannwhit1[1],3), np.round(mannwhit2[1],3)]}
    teams_dict[team] = team_dict

wilcoxon_high_low, wilcoxon_high_wind, wilcoxon_high_fb = [], [], []
mannwhit_high_low, mannwhit_high_wind, mannwhit_high_fb = [], [], []
for team in teams:
    if 0 < teams_dict[team]['Wilcoxon'][0] < 0.056:
        wilcoxon_high_low.append(team)
    if 0 < teams_dict[team]['Wilcoxon'][1] < 0.056:
        wilcoxon_high_wind.append(team)
    if 0 < teams_dict[team]['Wilcoxon'][2] < 0.056:
        wilcoxon_high_fb.append(team)
    if 0 < teams_dict[team]['Mannwhit'][0] < 0.056:
        mannwhit_high_low.append(team)
    if 0 < teams_dict[team]['Mannwhit'][1] < 0.056:
        mannwhit_high_wind.append(team)
    if 0 < teams_dict[team]['Mannwhit'][2] < 0.056:
        mannwhit_high_fb.append(team)
    

print(wilcoxon_high_low, wilcoxon_high_wind, wilcoxon_high_fb)

print(mannwhit_high_low, mannwhit_high_wind, mannwhit_high_fb)

game_mhl = pd.DataFrame(np.concatenate([games[games['STADIUM'] == team].values for team in mannwhit_high_low]), columns = games.columns)
game_mh = pd.DataFrame(np.concatenate([games[games['STADIUM'] == team].values for team in mannwhit_high_wind]), columns = games.columns)
game_mfb = pd.DataFrame(np.concatenate([games[games['STADIUM'] == team].values for team in mannwhit_high_fb]), columns = games.columns)
game_wfb = pd.DataFrame(np.concatenate([games[games['STADIUM'] == team].values for team in wilcoxon_high_fb]), columns = games.columns)
game_wh = pd.DataFrame(np.concatenate([games[games['STADIUM'] == team].values for team in wilcoxon_high_wind]), columns = games.columns)

def plot_significant_changes(game):
    for i,ga in enumerate(game['STADIUM'].unique()):
        game1 = game[game['STADIUM'] == ga]
        game1['Wind_Level'] = game1['Wind_Level'].astype('category')
        game1['Wind'] = game1['Wind'].astype('int')
        game1['Runs'] = game1['Runs'].astype('int')
        ax = sns.lmplot(x = 'Wind', y = 'Runs', hue = 'Wind_Level', truncate=True, data = game1)
        fig = ax.fig
        fig.subplots_adjust(top=0.9, wspace=0.1)
        t = fig.suptitle('Stadium : %s' % str(ga), fontsize=14)
        fig.show()

significant_stadiums = [game_mhl, game_mh, game_mfb, game_wfb, game_wh]
for stadium in significant_stadiums:
    plot_significant_changes(stadium)

# Run differences at Wrigley Field under different wind conditions
sns.distplot(games['Runs'][(games['STADIUM'] == 'CHN') & (games['Wind'] < 14) & (games['Wind'] >= 8)])
sns.distplot(games['Runs'][(games['STADIUM'] == 'CHN') & (games['Wind'] >= 14)])
sns.distplot(games['Runs'][(games['STADIUM'] == 'CHN') & (games['Wind'] < 8)])

