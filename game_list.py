#! python3
from selenium import webdriver
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
from datetime import date
from datetime import datetime
import time


games_total = pd.DataFrame(np.ones((1,12)), columns = ['date', 'team_away', 'team_home', 'pitcher_away', 'pitcher_home', 'expected_runs_away', 'actual_runs_away', 'expected_runs_home', 'actual_runs_home', 'temp', 'humidity', 'rain'])
from constant_variables import TEAM_INITIALS
def get_team_ini(team_ini):
    # Change format of team initials to match mlb.com
    for name, ini in TEAM_INITIALS.items():
        if ini == team_ini:
            return name
        
from constant_variables import LEAGUE
def get_team_league(team_ini):
    # Output if the team provided is in the American or National League
    for ini, league in LEAGUE.items():
        if ini == team_ini:
            return league
        
def change_header(header):
    # Change the category names in the header
    header[1], header[2], header[4], header[5] = 'Proj_Away_Runs', 'Runs_Away', 'Proj_Home_Runs', 'Runs_Home'
    return header

def assign_column_type(df, columns, column_type):
    df[columns] = df[columns].astype(column_type)
    return df

def fix_matchup(game1, game2):
    a, b, c, d, e, f = game1
    g, h, i, j, k, l = game2
    return (a, b, c, g, h, i), (d, e, f, j, k, l)

def check_double(a, b, c, d, e, f):
    # Checks if double header
    if c == f:
        return True
    else:
        False
        
def check_double1(a, b, c, d, e, f):
    # Check if game is a double header
    if c == f:
        return (a, b, c, d, e, f)

def double_headers(games, pre_or_post=0):
    # List of double headers (before and after duplicates were removed)
    doubles = list([x for x in games if check_double1(*x)])
    if pre_or_post == 0:
        return doubles[:len(doubles)//2]
    elif pre_or_post == 1:
        return doubles

def remove_games(games):
    # Remove repeat games without compromising index position
    for x in double_headers(games):
        games.reverse()        
        games.remove(x)
    return games

def fix_double_headers(games):
    # Put double headers against proper opponent
    i = 0
    double = double_headers(games)
    games = remove_games(games)
    while i in range(0, len(double)-1):
        switch = fix_matchup(double[i], double[i+1])
        games[games.index(double[i])] = switch[0]
        games[games.index(double[i+1])] = switch[1]
        i += 2
    return games

def clean_games(games):
    remove_games(games)
    fix_double_headers(games)
    return(games)
            
def average_wind(speed):
    # Output the average wind speed using the range provided
    try:
        re.search(r'([0-9]*)-([0-9]*)', str(speed)).group(2)
        speed1 = re.search(r'([0-9]*)-([0-9]*)', str(speed)).group(1)
        speed2 = re.search(r'([0-9]*)-([0-9]*)', str(speed)).group(2)
        return ((int(speed1) + int(speed2)) / 2)
    except AttributeError:
        return int(0)
    else:
        return int(speed1)
    
def average_column_value(df_column, digits, remove):
    # Finds a dfs column mean and rounds to users digit preference
    return round(df_column[df_column != remove].astype(float).mean(), digits)

traded_players = {'Chris Archer' : ['2018-07-31', 'TB', 'PIT'],
                  'Tyler Glasnow' : ['2018-07-31', 'PIT', 'TB'],
                  'Nathan Eovaldi' : ['2018-07-25', 'TB', 'BOS'],
                  'J.A. Happ' : ['2018-07-31', 'TOR', 'NYY'],
                  'Tyson Ross' : ['2018-08-05', 'SD', 'STL'],
                  'Lance Lynn' : ['2018-07-30', 'MIN', 'NYY'],
                  'Cole Hamels' : ['2018-06-27', 'TEX', 'CHC'],
                  'Mike Fiers' : ['2018-08-06', 'DET', 'OAK'],
                  'Jaime Garcia' : ['2018-08-04', 'TOR', 'CHC'],
                  'Gio Gonzalez' : ['2018-08-31', 'WAS', 'MIL'],
                  'Kevin Gausman' : ['2018-07-31', 'BAL', 'ATL'],
                  'Jordan Lyles' : ['2018-08-05', 'SD', 'MIL'],
                  'Luke Farrell' : ['2018-08-03', 'CHC', 'LAA'],
                  'Matthew Andriese' : ['2018-07-25', 'TB', 'ARI'],
                  'Jonny Venters' : ['2018-07-26', 'TB', 'ATL']
                  }

def trade_team(game):
    # Adjust for Trades
    if game[0] in traded_players and today_date < datetime.strptime(traded_players[game[0]][0]+' 12:30', '%Y-%m-%d %H:%M'):
        game = game[0:2]+(traded_players[game[0]][1],)+game[3:]
    if game[3] in traded_players and today_date < datetime.strptime(traded_players[game[3]][0]+' 12:30', '%Y-%m-%d %H:%M'):
        game = game[0:5]+(traded_players[game[3]][1],)
    return game

# missing  '2018-04-08' taken care of another way
shohei_ohtani_games =['2018-04-01', '2018-04-17', '2018-04-24', '2018-05-06', '2018-05-13', '2018-05-20', '2018-05-30', '2018-06-06', '2018-09-02']
shonei_placeholder = '(?:(?<!SP).*(?!LAA).*\d\">(\w*.\w*).*(?=RP).*(?=LAA).*(?=2<).*(?!SP).*(?!LAA))'
#(?:(?<=[0-9]{4}\">)|(?<=[0-9]{3}\">))(?:[A-Z][a-z]*|[?:A-Z\.]*?|(?:[A-Z][a-z]*.[A-Z][a-z]*)|([A-Z][a-z]*.[a-z]*.[a-z]*)).(?:(?:[A-Z][a-z]*)|(?:[a-z]*[A-Z][a-z]*)|(?:[A-Z][a-z]*-*?[A-Z][a-z]*))</a></td><td><span.style="color..683300">(SP)(?=\<).*?(?<=\D"\>)([A-Z]{2,3})(?=</td>).*?(?:(?<=[0-9]{4}\">)|(?<=[0-9]{3}\">))(?:[A-Z][a-z]*|[?:A-Z\.]*?|(?:[A-Z][a-z]*.[A-Z][a-z]*)|(?:[A-Z][a-z]*.[a-z]*.[a-z]*)).(?:(?:[A-Z][a-z]*)|(?:[a-z]*[A-Z][a-z]*)|(?:[A-Z][a-z]*[A-Z][a-z]*))</a></td><td><span.style="color..683300">(SP)(?=\<).*?(?<=\D"\>)([A-Z]{2,3})(?=</td>)|(?:(?<!SP).*(?!LAA).*\d\">(\w*.\w*).*(?=RP).*(?=LAA).*(?=2<).*(?!SP).*(?!LAA))

ohtani = ('Shohei Ohtani', 'SP', 'LAA')

def check_laa_bool(a, b, c, d, e, f, g, h):
    if (a == 'LAA' or d == 'LAA') and date_today.isoformat() in shohei_ohtani_games:
        return True
    
def check_last_game(games):
    for i, game in games:
        if check_laa_bool(*games) and i == len(games)-1:
            return True

def delete_laa(games):
    [games.remove(game) for game in games if check_laa_bool(*game)]
    return games

def delete_laa_weather(games):
    index = [games.index(game) for game in games if check_laa_bool(*game)]
    if len(index) > 0:
        game_table3.remove(game_table3[index[0]])
    return game_table3
            
def check_laa(a, b, c, d, e, f, g, h):
    if a == 'LAA' and date_today.isoformat() in shohei_ohtani_games:
        return (d,1)
    elif d == 'LAA' and date_today.isoformat() in shohei_ohtani_games:
        return(a,0)
        
def check_laa_bool1(a, b, c, d, e, f):
    if (a == 'LAA' or d == 'LAA') and date_today.isoformat() in shohei_ohtani_games:
        return True

def return_game(games):
    return [check_laa(*x) for x in games if check_laa(*x)]

def add_laa(a, b, c, d, e, f):
    x,y = return_game(game_table2)[0]
    if c == x and y == 0:
        return (a, b, c,) + ohtani
    elif c == x and y == 1:
        return ohtani + (a, b, c,)
    elif f == x and y == 0:
        return (d, e, f,) + ohtani
    elif f == x and y == 1:
        return ohtani + (d, e, f,)
    else:
        exit

def fix_games(games):
    new_table = []
    x,y = return_game(game_table2)[0]
    for i,game in enumerate(games):
        if game[2] == x and y == 0:
            if check_last_game(game_table2):
                new_table.append(game[:3] + ohtani)
            else:
                z = i
                new_table.append(game[:3] + ohtani)
                while z < len(games)-1:
                    new_table.append(games[z][3:] + games[z+1][:3])
                    z += 1
            if game[2] == x and y == 1:
                if check_last_game(game_table2):
                    new_table.append(ohtani + game[3:])
                else:
                    z = i
                    new_table.append(ohtani + game[3:])
                    while z <= len(games)-1:
                        new_table.append(games[z][:3] + games[z+1][3:])
                        z += 1
    return new_table

def remove_laa_opponent(games):
    # Remove Othani opponent and delete last game if a team is cut off
    index = [game_table2.index(game) for game in game_table2 if check_laa_bool(*game)]
    if len(index) > 0:
        games, del_game = laa_last_game(games)
        return games, del_game
    else:
        del_game = False
        return games, del_game

def delete_last_game(games):
    games = games[:-1]
    return games

def laa_last_game(games):
    # Remove last game if team is cut off
    table5 = np.ravel(games)
    table5_reshape = np.reshape(np.ravel(games),(len(np.ravel(games))//3,3))
    i = np.where(table5 == return_game(game_table2)[0][0])[0]
    if len(i) > 0 and i < len(table5)-6:
        table5_reshape = np.delete(table5_reshape, [i-2, i-1, i])
        table5_reshape = np.reshape(np.ravel(table5_reshape[:-3]),(len(np.ravel(table5_reshape))//6,6))
        table5_new = [tuple(game) for game in table5_reshape]
        del_game = True
        return table5_new, del_game
    else:
        del_game = False
        games = games
    return games, del_game

def atlanta_fix(games):
    if date_today.isoformat() == '2018-05-01':
        del_game = True
        games = games[:-1]
        return games, del_game
    else:
        del_game = False
        games = games
        return games, del_game

def delete_atl_stats(games):
    if del_game:
        [games.remove(game) for game in games if 'ATL' in game]
    return games

def delete_atl_weather(games):
    if del_game:
        index = [games.index(game) for game in games if 'ATL' in game]
        if len(index) > 0:
            game_table3.remove(game_table3[index[0]])
    return game_table3

def add_half_game(date, table):
    if ((date_today.isoformat() == date) & (('Noah Syndergaard', 'SP', 'NYM') in table)):
        table.insert(table.index(('Noah Syndergaard', 'SP', 'NYM')),('Michael Soroka', 'SP', 'ATL'))
        table.remove(('Shohei Ohtani', 'SP', 'LAA'))
        return table
    else:
        return table
    
def remake_table(table, table1, date):
    if date_today.isoformat() in date:
        return [table[i] + table[i+1] for i in range(0, len(table), 2)]
    else:
        return table1

def add_4_24(date, table):
    if date.isoformat() == '2018-04-24':
        table.insert(table.index(('Tyler Mahle', 'SP', 'CIN')),('Brandon McCarthy', 'SP', 'ATL'))
        table.insert(table.index(('Kyle Freeland', 'SP', 'COL')),('Eric Lauer', 'SP', 'SD'))
        table.remove(('Charlie Morton', 'SP', 'HOU'))
        return table
    if date.isoformat() == '2018-05-03':
        table.append(('Wade LeBlanc', 'SP', 'SEA'))
        table.insert(table.index(('Mike Fiers', 'SP', 'OAK')),('Lance McCullers', 'SP', 'HOU'))
        table.remove(('Shohei Ohtani', 'SP', 'LAA'))
        return table
    if date.isoformat() == '2018-04-08':
        table.insert(table.index(('Matt Harvey', 'SP', 'CIN')),('Shohei Ohtani', 'SP', 'LAA'))
        return table
    else:
        return table
    
def remove_ohtani(date, table):
    if (date.isoformat() not in shohei_ohtani_games) and ('Shohei Ohtani' in np.ravel(table) and (date.isoformat() != '2018-04-08')):
        new = [(str(np.ravel(table)[i]), str(np.ravel(table)[i+1]), str(np.ravel(table)[i+2])) for i in range(0, len(np.ravel(table)), 3) if np.ravel(table)[i] != 'Shohei Ohtani']
        if game_table4[-1:][0] not in new:
            new.append(game_table4[-1:][0])
            return [new[i] + new[i+1] for i in range(0, len(new), 2)]
    else:
        return table


#date_start = int(input("Input Date to Work Back From (yyyy): ")), int(input("Input Date to Work Back From (mm): ")), int(input("Input Date to Work Back From (dd): "))
date_finish = int(input("Input Date to End on (yyyy): ")), int(input("Input Date to End on (m): ")), int(input("Input Date to End on (d): "))
#file_name = input('Name of file to save game data under: ')

# Set arbitrary date        
date_today = 1

# Scrape game data for each day
options = webdriver.ChromeOptions()
options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(chrome_options=options)
driver.get("https://baseballmonster.com/boxscores.aspx")
driver.find_element_by_name("BACK").click()
time.sleep(2)

# Start Scraping
while date_today != date(date_finish[0], date_finish[1], date_finish[2]):

    # Scrape the current page
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    # Number of Games
    view = soup.find_all('a', string = 'View')        
    games_day = len(view)
    
    # Check if games were played this day
    if games_day > 0:    
        # Game Categories
        th = soup.find_all('th')
        header, game = [], []
        for i,row in enumerate(th[:50]):
            if row.string == 'Away':
                header = [th[x].string for x in range(i,i+9)]
                header = change_header(header)
        
        # Split by game
        table1 = soup.select('tbody')
        pattern = re.compile(r"<tbody>(.*)</tbody>", flags=re.S)
        game_table1 = [pattern.findall(str(game)) for game in table1]
        pattern = re.compile(r"<td>.*?<td>([A-Z]{2,3})</td><td.*?>.*?(\d*.\d|odds).*?</td><td.*?>.(\d*)</td><td>@.([A-Z]{2,3})</td><td.*?>.*?(\d.*?.\d|odds).*?</td><td.*?>.(\d*)</td><td.*?>.*?([0-9]*:[0-9]{2}..)</td><td.*?>([A-Z][a-z]*?)</td>")
        game_table2 = [pattern.findall(str(game)) for game in game_table1 if game[0][0:16] == "<tr><td><a href="][0]
        pattern = re.compile(r"<td><div class=\"weather\">.*?(\d{1,3})°.*?(\d{1,3})%.*?\"(Winds|).*?([a-z]*.-.[a-z]*|[a-z]{2,3}.*?|[a-z]*-[a-z]*).*?.([A-Z]{2}|at|<).*?([0-9]*-[0-9]*|>).*?\"|Final</td><td><img alt=\"([A-Z][a-z]*.[A-Z]*[a-z]*?)\"", flags=re.S)
        game_table3 = [pattern.findall(str(game)) for game in game_table1 if game[0][0:16] == "<tr><td><a href="][0]
        pattern = re.compile(r"=[0-9]{3,5}\">([A-Z][a-z]*?.[A-Z][a-z]*?|[A-Z].[A-Z]..[A-Z][a-z]*?)(?=</a></td><td><span style=\"color..683300\">(SP)</span>).*?\">([A-Z]{2,3})</td>.*?")
        game_table4 = [pattern.findall(str(game)) for game in game_table1 if game[0][0:20] == '<tr><td colspan="2">'][0]
        pattern = re.compile(r'(?:(?<=[0-9]{4}\">)|(?<=[0-9]{3}\">))((?:[A-Z][a-z]*|[?:A-Z\.]*?|(?:[A-Z][a-z]*.[A-Z][a-z]*)|(?:[A-Z][a-z]*.[a-z]*.[a-z]*)).(?:(?:[A-Z][a-z]*)|(?:[a-z]*[A-Z][a-z]*)|(?:[A-Z][a-z]*-*?[A-Z][a-z]*)))</a></td><td><span.style="color..683300">(SP)(?=\<).*?(?<=\D"\>)([A-Z]{2,3})(?=</td>).*?(?:(?<=[0-9]{4}\">)|(?<=[0-9]{3}\">))((?:[A-Z][a-z]*|[?:A-Z\.]*?|(?:[A-Z][a-z]*.[A-Z][a-z]*)|(?:[A-Z][a-z]*.[a-z]*.[a-z]*)).(?:(?:[A-Z][a-z]*)|(?:[a-z]*[A-Z][a-z]*)|(?:[A-Z][a-z]*[A-Z][a-z]*)))</a></td><td><span.style="color..683300">(SP)(?=\<).*?(?<=\D"\>)([A-Z]{2,3})(?=</td>)')
        game_table5 = [pattern.findall(str(game)) for game in game_table1 if game[0][0:20] == '<tr><td colspan="2">'][0]

        # Today's Date
        current_date = soup.find_all('h1', string=True)
        pattern = re.compile(r"([0-9]*?)(/)([0-9]*?)(/)([0-9]{4})")
        date_today = date(int(pattern.search(str(current_date[0])).group(5)), int(pattern.search(str(current_date[0])).group(1)), int(pattern.search(str(current_date[0])).group(3)))
        today_date = datetime(int(pattern.search(str(current_date[0])).group(5)), int(pattern.search(str(current_date[0])).group(1)), int(pattern.search(str(current_date[0])).group(3)), 12, 30)
        
        # Add Missing Pitchers
        game_table4 = add_half_game('2018-05-01', game_table4)
        game_table4 = add_4_24(date_today, game_table4)
        game_table5 = remake_table(table=game_table4, table1=game_table5, date=['2018-05-01', '2018-04-24', '2018-05-03', '2018-04-08'])
        game_table5 = remove_ohtani(date_today, game_table5)

        # Trade Players
        game_table5 = [trade_team(game) for game in game_table5]
        
        # Delete LAA Ohtani games until fixed
        game_table5, del_game = remove_laa_opponent(game_table5)
        game_table3 = delete_laa_weather(game_table2)
        game_table2 = delete_laa(game_table2)
        
        # Fix double headers
        game_table5 = fix_double_headers(game_table5)
        if del_game:
            game_table2 = delete_last_game(game_table2)
            game_table3 = delete_last_game(game_table3)
        
        # DataFrame of Game Data
        game_info = pd.DataFrame(game_table2, columns = header[:-1])
        game_weather = pd.DataFrame(game_table3, columns = ['Temp', 'Humidity', 'Wind', 'Direction', 'Location', 'MPH', 'Stadium'])
        starting_pitchers = pd.DataFrame(game_table5, columns = ['Starting_Pitcher_Away', 'Position1', 'Team_Away', 'Starting_Pitcher_Home', 'Position2', 'Team_Home'])
        
        # Set Dome conditions
        game_weather['Temp'][game_weather['Stadium'] != ''] = int(75)
        game_weather['Humidity'][game_weather['Humidity']  == 'NaN'] = int(70)
        game_weather['Humidity'][game_weather['Stadium'] != ''] = int(70)
        game_weather['Wind'][game_weather['MPH'] == ''] = int(0)
        game_weather['Location'][game_weather['Direction'] == 'right-left'] = 'RL'
        game_weather['Location'][game_weather['Direction'] == 'left-right'] = 'LR'
        game_weather['Location'][game_weather['Direction'] == ('ain' or 'rain-array' or 'tor' or '')] = 'None'
        game_weather['Direction'][game_weather['Direction'] == ('ain' or 'rain-array' or 'tor' or '')] = 'None'       
        game_weather['Direction'][game_weather['Stadium'] == ('Dome' or 'Roof Closed')] = 'None'
        game_weather['Location'][game_weather['Stadium'] == ('Dome' or 'Roof Closed')] = 'None'
        game_weather['MPH'][game_weather['Stadium'] == ('Dome' or 'Roof Closed')] = int(0)
        game_weather['MPH'][game_weather['MPH'] == '>'] = int(0)
        game_weather['Location'][game_weather['Location'] == '<'] = int(0)
        
        
        # Combine game_info and game weather
        game_final = pd.concat((game_info, game_weather, starting_pitchers), axis = 1)
        
        # Add date and league to game data and update format of team initials
        game_final['Date'] = date_today
        game_final['Away'] = list(map((lambda x:get_team_ini(x)), game_final['Away']))
        game_final['Home'] = list(map((lambda x:get_team_ini(x)), game_final['Home']))
        game_final['league'] = list(map((lambda x:get_team_league(x)), game_final['Home']))
        game_final['Wind'] = list(map((lambda x:average_wind(x)), game_final['MPH']))
        game_final['Temp'][pd.isna(game_final['Temp'])] = int(75)
        game_final['Humidity'][pd.isna(game_final['Humidity'])] = int(70)
        game_final['Proj_Away_Runs'][game_final['Proj_Away_Runs'] == 'odds'] = average_column_value(game_final['Proj_Away_Runs'], 1, 'odds')
        game_final['Proj_Home_Runs'][game_final['Proj_Home_Runs'] == 'odds'] = average_column_value(game_final['Proj_Home_Runs'], 1, 'odds')        
        game_final = assign_column_type(game_final, ['Proj_Away_Runs', 'Proj_Home_Runs', 'Wind'], float)
        game_final = assign_column_type(game_final, ['Runs_Away', 'Runs_Home', 'Temp', 'Humidity'], int)
        game_final['Starting_Pitcher_Away'] = list(map((lambda x:str(x).upper()), game_final['Starting_Pitcher_Away']))
        game_final['Starting_Pitcher_Home'] = list(map((lambda x:str(x).upper()), game_final['Starting_Pitcher_Home']))

    
        # Add today's games to dataframe with all games
        try: 
            games_by_date = pd.concat((games_by_date.iloc[:, :len(game_final.columns)], game_final), axis = 0)
        except NameError:
            games_by_date = game_final

    # Go to next day
    driver.find_element_by_name("BACK").click()
    time.sleep(2)
    
driver.quit()

games_by_date.to_csv('CSV/games_by_date.csv', mode='w', index=False, header=True)

print('I have collected all of the information you requested and saved it in your prefered destination')
