from ast import Delete
from datetime import date
from datetime import timedelta
import pandas as pd
import sqlite3
import sqlalchemy as db
import constants
import logging

today = date.today()
yesterday = today - timedelta(days = 1)
year = today.year
last_year = year - 1
next_year = year + 1
current_date = today.strftime('%B X%d, %Y (%A)').replace('X0','X').replace('X','')
yesterday_date = yesterday.strftime('%B X%d, %Y (%A)').replace('X0','X').replace('X','')

#current_date = "September 1, 2022 (Thursday)" #testing
#yesterday_date = "Auguest 31, 2022 (Wednesday)" #testing
#year = 2020 #testing
#last_year = 2019 #testing

team = "Louisiana Tech"

sql_db=constants.sql_db

#Todo: refactor 
engine = db.create_engine(sql_db)
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

def get_tech_url(sport):
    if sport in {'mens-basketball', 'womens-basketball', 'womens-tennis', 'womens-bowling', 'mens-golf'}:
        if date(year,1,1) <= today <= date(year,6,20):
            url_year = str(last_year) + "-" + str(year)[2:]
        if date(year,6,21) <= today <= date(year,12,31):    
            url_year = str(year) + "-" + str(next_year)[2:]
    if sport in {'baseball', 'womens-soccer', 'softball', 'womens-volleyball', 'football', 'womens-cross-country', 'mens-cross-country', 'womens-track-and-field', 'mens-track-and-field'}:
        url_year = year
        if sport in {'womens-cross-country', 'mens-cross-country', 'womens-track-and-field', 'mens-track-and-field'}:
            sport = sport.split("-", 1)[1]
    url = 'https://latechsports.com/sports/{}/schedule/{}?grid=true'.format(sport,url_year)
    return url

'''def get_cusa_url(sport):
    if sport == 'softball':
        url_id = '107'
    url = 'https://https://conferenceusa.com/standings.aspx?standings={}'.format(url_id)
    return url 
'''

def get_game_data(url, sport):
    try:
        df = pd.read_html(url, header=0)[0]
        recent_games = df[df.Date.isin([current_date, yesterday_date])].where(pd.notnull(df), None)
    except AttributeError:
        logging.info("Current year schedule for this sport has not been created yet!")
        return
    else:
        if recent_games.empty:
            logging.info("Tech did not play recently in this sport!")
            return   
        tech_games = recent_games[~recent_games.Opponent.str.contains("vs.")]
        game_info = tech_games[['Date', 'Time', 'Opponent', 'At', 'Result']]
        game_info.insert(0, 'Sport', sport.capitalize())
        games = game_info.values.tolist()
        logging.info("Tech played recently in this sport!")
        return games

def is_game_exhibition(opponent):
    exhibition = False
    if "(exhibition)" in opponent:
        exhibition = True
        logging.info("This Tech game is an exhibition; no tweet needed!")
    else:
        logging.info("This Tech game is not an exhibition!")
    return exhibition

def is_game_final(result):
    final = False
    if not result != result and result not in {None, 'Canceled', 'Postponed'}:
        final = True
        logging.info("This Tech game is final!")
    else:
        logging.info("This Tech game is not final!\nResult: {}".format(result))
    return final

'''def result_to_score(sport, result):
    if sport in {'Baseball', 'Womens-soccer', 'Softball', 'Womens-volleyball', 'Football', 'Mens-basketball', 'Womens-basketball', 'Womens-tennis'}:
        win_loss = result[0]
        score = result[4:]
        if " " in score:
            split_score = score.split(" ", 1)
            score = split_score[0]
        tech_score = int(score.split("-")[0])
        away_score = int(score.split("-")[1])
        if (win_loss == 'W' and away_score >= tech_score) or (win_loss == 'L' and away_score <= tech_score):
                away_score,tech_score=tech_score,away_score'''
        

def is_game_in_db(gd_sport, gd_date, gd_time, gd_opponent, gd_home_away, gd_result):
    query = db.select([games]).where(db.and_(games.columns.Sport == gd_sport, games.columns.Date == gd_date, games.columns.Time == gd_time, games.columns.Opponent == gd_opponent, games.columns.At == gd_home_away, games.columns.Result == gd_result))
    result = engine.execute(query).fetchall()
    if not result:
        logging.info("Tweet is not a duplicate!")
        logging.info("Result: " + str(result))
        return False
    logging.info("Tech played recently in this sport, but it was already tweeted!")
    return True

def set_tweet(sport, opponent, home_away, result):
    team_sport = get_team_sport(sport)
    if sport in {'Womens-bowling', 'Mens-golf', 'Mens-track-and-field', 'Womens-track-and-field', 'Mens-cross-country', 'Womens-cross-country'}:
        if sport in {'Mens-track-and-field', 'Mens-cross-country', 'Womens-track-and-field', 'Womens-cross-country'}:
            results = result.split(';')
            if sport in {'Mens-track-and-field', 'Mens-cross-country'}:
                result = results[0][3:]
            if sport in {'Womens-track-and-field', 'Womens-cross-country'}:
                result = results[1][3:]
        if result == '1st':
            tweet = "No.\n{}: {} finished {} at the {}.\n".format(team_sport, team, result, opponent)
        else:
            tweet = "Yes.\n{}: {} finished {} at the {}.\n".format(team_sport, team, result, opponent)
    if sport in {'Baseball', 'Womens-soccer', 'Softball', 'Womens-volleyball', 'Football', 'Mens-basketball', 'Womens-basketball', 'Womens-tennis'}:
        win_loss = result[0]
        score = result[4:]
        if " " in score:
            split_score = score.split(" ", 1)
            score = split_score[0]
        if home_away in {'Home', 'Neutral'}:
            tech_score = int(score.split("-")[0])
            away_score = int(score.split("-")[1])
            if (win_loss == 'W' and away_score >= tech_score) or (win_loss == 'L' and away_score <= tech_score):
                away_score,tech_score=tech_score,away_score
            if win_loss == 'W':
                tweet = "No.\n{}: {} defeats {} {} to {}.".format(team_sport, team, opponent, tech_score, away_score) 
            if win_loss == 'T':
                tweet = "No.\n{}: {} ties {} {} to {}.".format(team_sport, team, opponent, tech_score, away_score)
            if win_loss == 'L':
                tweet = "Yes.\n{}: {} defeats {} {} to {}.".format(team_sport, opponent, team, away_score, tech_score) 
        if home_away in {'Away'}:
            home_score = str(score.split("-")[1])
            tech_score = str(score.split("-")[0])
            if (win_loss == 'W' and home_score >= tech_score) or (win_loss == 'L' and home_score <= tech_score):
                home_score,tech_score=tech_score,home_score
            if win_loss == 'W':
                tweet = "No.\n{}: {} defeats {} {} to {}.".format(team_sport, team, opponent, tech_score, home_score)
            if win_loss == 'T':
                tweet = "No.\n{}: {} ties {} {} to {}.".format(team_sport, team, opponent, tech_score, home_score)
            if win_loss == 'L':
                tweet = "Yes.\n{}: {} defeats {} {} to {}.".format(team_sport, opponent, team, home_score, tech_score) 
    return tweet

def get_team_sport(sport):
    if sport == 'Football':
        team_sport = "🏈"
    if sport == 'Mens-basketball':
        team_sport = "Men's 🏀"
    if sport == 'Womens-basketball':
        team_sport = "Women's 🏀"
    if sport == "Baseball":
        team_sport = "⚾"
    if sport == "Softball":
        team_sport = "🥎"
    if sport == "Womens-soccer":
        team_sport = "⚽"
    if sport == 'Womens-volleyball':
        team_sport = "🏐"
    if sport == 'Womens-tennis':
        team_sport = "🎾"
    if sport == 'Mens-golf':
        team_sport = "⛳"
    if sport == "Womens-bowling":
        team_sport = "🎳"
    if sport == "Mens-track-and-field":
        team_sport = "Men's T&F 🏃"
    if sport == "Womens-track-and-field":
        team_sport = "Women's T&F 🏃"
    if sport == "Mens-cross-country":
        team_sport = "Men's XC 🏃"
    if sport == "Womens-cross-country":
        team_sport = "Women's XC 🏃"
    return team_sport

def update_game_data(sport, date, time, opponent, home_away, result):
    #Insert new game data
    insert_query = db.insert(games).values(Sport=sport, Date=date, Time=time, Opponent=opponent, At=home_away, Result=result)
    engine.execute(insert_query)
    logging.info("New game data inserted!")
    #Delete old game data
    all_games = db.select([games])
    result = engine.execute(all_games).fetchall()
    for game in result:
        sport, date, time, opponent, home_away, result = game[0], game[1], game[2], game[3], game[4], game[5]
        if date != yesterday_date and date != current_date:
            delete_query = db.delete(games).where(db.and_(games.columns.Sport == sport, games.columns.Date == date, games.columns.Time == time, games.columns.Opponent == opponent, games.columns.At == home_away, games.columns.Result == result))
            engine.execute(delete_query)
            logging.info("Old game data deleted!")
