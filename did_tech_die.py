from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
import pandas as pd

today = date.today()
yesterday = today - timedelta(days=1)
year = today.year
last_year = year - 1
current_date = today.strftime('%B X%d, %Y (%A)').replace('X0','X').replace('X','')
yesterday_date = yesterday.strftime('%B X%d, %Y (%A)').replace('X0','X').replace('X','')

#current_date = "September 17, 2021 (Friday)" #testing
team = "Louisiana Tech"

def get_sport_url(sport):
    if sport in {'mens-basketball', 'womens-basketball', 'womens-tennis'}:
        url_year = str(last_year) + "-" + str(year)[2:]
    if sport in {'baseball', 'womens-soccer', 'softball', 'womens-volleyball', 'football'}:
        url_year = year
    url = 'https://latechsports.com/sports/{}/schedule/{}?grid=true'.format(sport,url_year)
    return url

def get_game_data(url):
    df = pd.read_html(url, header=0)[0]
    recent_games = df[df.Date.isin([current_date, yesterday_date])].where(pd.notnull(df), None)
    if recent_games.empty:
        print("Tech did not play recently in this sport!\n")
        return    
    tech_games = recent_games[~recent_games.Opponent.str.contains("vs.")]
    print("Tech played/plays recently in this sport!\n")
    return tech_games

def get_record(url):
    page = requests.get(url+".html")
    soup = BeautifulSoup(page.content, 'html.parser')
    record = soup.findAll('span', class_="flex-item-1")[1].text
    return record

def is_game_final(game):
    final = False
    result = game[2]
    if result not in {None, 'Canceled', 'Postponed'}:
        final = True
        print("This Tech game is final!\n")
    else:
        print("This Tech game is not final!\nResult: {}".format(result))
    return final

#Todo: account for doubleheaders
def get_resulting_tweet(sport, game, record):
    if sport == 'football':
        team_sport = "🏈"
    if sport == 'mens-basketball':
        team_sport = "Men's 🏀"
    if sport == 'womens-basketball':
        team_sport = "Women's 🏀"
    if sport == "baseball":
        team_sport = "⚾"
    if sport == "softball":
        team_sport = "🥎"
    if sport == "womens-soccer":
        team_sport = "⚽"
    if sport == 'womens-volleyball':
        team_sport = "🏐"
    if sport == 'womens-tennis':
        team_sport = "🎾"
    home_away = game[1]
    win_loss = game[2][0]
    opponent = game[0]
    score = game[2][4:]
    if " " in score:
        split_score = score.split(" ", 1)
        score = split_score[0]
    if home_away in {'Home', 'Neutral'}:
        home_score = str(score.split("-")[0])
        away_score = str(score.split("-")[1])
        if win_loss == 'W':
            result = "No.\n{}: {} defeats {} {} to {}.\nTech's overall record is now {}.".format(team_sport, team, opponent, home_score, away_score, record) 
        else:
            result = "Yes.\n{}: {} defeats {} {} to {}.\nTech's overall record is now {}.".format(team_sport, opponent, team, away_score, home_score, record) 
    else:
        home_score = str(score.split("-")[1])
        away_score = str(score.split("-")[0])
        if win_loss == 'W':
            result = "No.\n{}: {} defeats {} {} to {}.\nTech's overall record is now {}.".format(team_sport, team, opponent, away_score, home_score, record)
        else:
            result = "Yes.\n{}: {} defeats {} {} to {}.\nTech's overall record is now {}.".format(team_sport, opponent, team, home_score, away_score, record) 
    return result