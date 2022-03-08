import re
import time
import pandas as pd

now = time.localtime()
year = now.tm_year
last_year = year - 1
current_date = time.strftime("%B%e, %Y (%A)",now)
#current_date = "March 2, 2022 (Wednesday)" testing
team = "Louisiana Tech"

def get_game_data():
    url_year = str(last_year) + "-" + str(year)[2:]
    url = 'https://latechsports.com/sports/mens-basketball/schedule/{}?grid=true'.format(url_year)
    df = pd.read_html(url, header=0)[0]
    games_today = df[df.Date.isin([current_date])]
    if games_today.empty:
        print("Tech MBB does not play today!")
        return
    return games_today

def is_game_final(games_today):
    final = False
    game_info = games_today[['Result']]
    if game_info.values.tolist()[0] != 'NaN':
        final = True
        print("Today's Tech MBB game is final!")
    else:
        print("Today's Tech MBB game is not final!")
    return final

def get_resulting_tweet(games_today):
    game_info = games_today[['Opponent', 'At', 'Result']]
    game = game_info.values.tolist()
    home_away = game[0][1]
    win_loss = game[0][2][0]
    opponent = game[0][0]
    score = game[0][2][4:]
    if home_away == 'Home':
        home_score = str(score.split("-")[0])
        away_score = str(score.split("-")[1])
        if win_loss == 'W':
            result = "No.\nMen's 🏀: {} {}, {} {}".format(team, home_score, opponent, away_score) 
        else:
            result = "Yes.\nMen's 🏀: {} {}, {} {}".format(opponent, away_score, team, home_score) 
    else:
        home_score = str(score.split("-")[1])
        away_score = str(score.split("-")[0])
        if win_loss == 'W':
            result = "No.\nMen's 🏀: {} {}, {} {}".format(team, away_score, opponent, home_score)
        else:
            result = "Yes.\nMen's 🏀: {} {}, {} {}".format(opponent, home_score, team, away_score) 
    return result