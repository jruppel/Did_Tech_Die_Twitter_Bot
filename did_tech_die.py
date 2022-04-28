from datetime import date
from datetime import timedelta
import pandas as pd
import sqlite3
import sqlalchemy as db

today = date.today()
yesterday = today - timedelta(days = 1)
year = today.year
last_year = year - 1
current_date = today.strftime('%B X%d, %Y (%A)').replace('X0','X').replace('X','')
yesterday_date = yesterday.strftime('%B X%d, %Y (%A)').replace('X0','X').replace('X','')

#current_date = "April 23, 2022 (Saturday)" #testing
#yesterday_date = "April 24, 2022 (Sunday)" #testing
team = "Louisiana Tech"

#Todo: refactor 
engine = db.create_engine('sqlite:///gamedata.db')
connection = engine.connect()
metadata = db.MetaData(engine)
if not db.inspect(engine).has_table('games'):
    db.Table('games', metadata,
          db.Column('Sport', db.String), 
          db.Column('Date', db.String), 
          db.Column('Time', db.String),
          db.Column('Opponent', db.String), 
          db.Column('At', db.String),
          db.Column('Result', db.String)
    )
    metadata.create_all()
games = db.Table('games', metadata, autoload=True, autoload_with=engine)

def get_sport_url(sport):
    if sport in {'mens-basketball', 'womens-basketball', 'womens-tennis'}:
        url_year = str(last_year) + "-" + str(year)[2:]
    if sport in {'baseball', 'womens-soccer', 'softball', 'womens-volleyball', 'football'}:
        url_year = year
    url = 'https://latechsports.com/sports/{}/schedule/{}?grid=true'.format(sport,url_year)
    return url

def get_game_data(url, sport):
    df = pd.read_html(url, header=0)[0]
    recent_games = df[df.Date.isin([current_date, yesterday_date])].where(pd.notnull(df), None)
    if recent_games.empty:
        print("Tech did not play recently in this sport!\n")
        return    
    tech_games = recent_games[~recent_games.Opponent.str.contains("vs.")]
    game_info = tech_games[['Date', 'Time', 'Opponent', 'At', 'Result']]
    sport_info = sport.capitalize()
    game_info.insert(0, 'Sport', sport_info)
    games = game_info.values.tolist()
    print("Tech played/plays recently in this sport!\n")
    return games

def is_game_final(game):
    final = False
    result = game[5]
    if result not in {None, 'Canceled', 'Postponed'}:
        final = True
        print("This Tech game is final!")
    else:
        print("This Tech game is not final!\nResult: {}".format(result))
    return final

def is_game_in_db(game):
    gd_sport = game[0]
    gd_date = game[1]
    gd_time = game[2]
    gd_opponent = game[3]
    gd_at = game[4]
    gd_result = game[5]
    query = db.select([games]).where(db.and_(games.columns.Sport == gd_sport, games.columns.Date == gd_date, games.columns.Time == gd_time, games.columns.Opponent == gd_opponent, games.columns.At == gd_at, games.columns.Result == gd_result))
    result = engine.execute(query).fetchall()
    print(result)
    if not result:
        return False
    print("Tech played recently in this sport, but it was already tweeted!\n")
    return True

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
    home_away = game[4]
    win_loss = game[5][0]
    opponent = game[3]
    score = game[5][4:]
    if " " in score:
        split_score = score.split(" ", 1)
        score = split_score[0]
    if home_away in {'Home', 'Neutral'}:
        home_score = str(score.split("-")[0])
        away_score = str(score.split("-")[1])
        if win_loss == 'W':
            result = "No.\n{}: {} defeats {} {} to {}.".format(team_sport, team, opponent, home_score, away_score) 
        else:
            result = "Yes.\n{}: {} defeats {} {} to {}.".format(team_sport, opponent, team, away_score, home_score) 
    else:
        home_score = str(score.split("-")[1])
        away_score = str(score.split("-")[0])
        if win_loss == 'W':
            result = "No.\n{}: {} defeats {} {} to {}.".format(team_sport, team, opponent, away_score, home_score)
        else:
            result = "Yes.\n{}: {} defeats {} {} to {}.\n".format(team_sport, opponent, team, home_score, away_score) 
    return result

def update_game_data(game_data):
    #Insert new game data
    insert_query = db.insert(games).values(Sport=game_data[0], Date=game_data[1], Time=game_data[2], Opponent=game_data[3], At=game_data[4], Result=game_data[5])
    engine.execute(insert_query)
    #Delete old game data
    all_games = db.select([games])
    result = engine.execute(all_games).fetchall()
    for game in result:
        if game[1] != yesterday_date or game[1] != current_date:
            delete_query = db.delete(games).where(db.and_(games.columns.Sport == game[0], games.columns.Date == game[1], games.columns.Time == game[2], games.columns.Opponent == game[3], games.columns.At == game[4], games.columns.Result == game[5]))
            engine.execute(delete_query)