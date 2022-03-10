import time
import pandas as pd

now = time.localtime()
year = now.tm_year
last_year = year - 1
current_date = time.strftime("%B%e, %Y (%A)",now)
#current_date = "September 17, 2021 (Friday)" #testing
team = "Louisiana Tech"

def get_todays_game_data(sport):
    if sport in {'mens-basketball', 'womens-basketball', 'womens-tennis'}:
        url_year = str(last_year) + "-" + str(year)[2:]
    if sport in {'baseball', 'womens-soccer', 'softball', 'womens-volleyball', 'football'}:
        url_year = year
    url = 'https://latechsports.com/sports/{}/schedule/{}?grid=true'.format(sport,url_year)
    df = pd.read_html(url, header=0)[0]
    games_today = df[df.Date.isin([current_date])].where(pd.notnull(df), None)
    if games_today.empty:
        print("Tech does not play today in this sport!\n")
        return
    tech_games_today = games_today[~games_today.Opponent.str.contains("vs.")]
    print("Tech plays today for this sport!\n")
    return tech_games_today

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
def get_resulting_tweet(sport, game):
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
    print(game)
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
            result = "No.\n{}: {} {}, {} {}".format(team_sport, team, home_score, opponent, away_score) 
        else:
            result = "Yes.\n{}: {} {}, {} {}".format(team_sport, opponent, away_score, team, home_score) 
    else:
        home_score = str(score.split("-")[1])
        away_score = str(score.split("-")[0])
        if win_loss == 'W':
            result = "No.\n{}: {} {}, {} {}".format(team_sport, team, away_score, opponent, home_score)
        else:
            result = "Yes.\n{}: {} {}, {} {}".format(team_sport, opponent, home_score, team, away_score) 
    return result