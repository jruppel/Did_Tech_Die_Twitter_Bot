# Manage DB
import constants
import sqlalchemy as db

sql_db,logging,yesterday_date,current_date=constants.sql_db,constants.logging,constants.yesterday_date,constants.current_date

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
          db.Column('Result', db.String),
          db.Column('ID', db.String)
    )
    metadata.create_all()
games = db.Table('games', metadata, autoload=True, autoload_with=engine)

def is_game_in_db(gd_sport, gd_date, gd_time, gd_opponent, gd_home_away, gd_result):
    result = get_game_data(gd_sport, gd_date, gd_time, gd_opponent, gd_home_away, gd_result)
    if not result:
        logging.info("Tweet is not a duplicate!")
        return False
    logging.info("Tech played recently in this sport, but it was already tweeted!")
    return True

def get_game_data(sport, date, time, opponent, home_away, result):
    if not [x for x in (sport, time, opponent, home_away) if x is None] and result is None:
        query = db.select([games]).where(db.and_(games.columns.Sport==sport,games.columns.Date== date,games.columns.Time==time,games.columns.Opponent==opponent,games.columns.At==home_away))
    if not [x for x in (sport, time, result, home_away) if x is None] and opponent is None:
        query = db.select([games]).where(db.and_(games.columns.Sport==sport,games.columns.Date == date, games.columns.Time == time, games.columns.At == home_away, games.columns.Result == result))
    if not [x for x in (sport, time, opponent, home_away, result) if x is None]:
        query = db.select([games]).where(db.and_(games.columns.Sport==sport,games.columns.Date == date, games.columns.Time == time, games.columns.Opponent == opponent, games.columns.At == home_away, games.columns.Result == result))
    all_games = engine.execute(query).fetchall()
    return all_games

def insert_game_data(sport, date, time, opponent, home_away, result, id):
    #Insert new game data
    insert_query = db.insert(games).values(Sport=sport, Date=date, Time=time, Opponent=opponent, At=home_away, Result=result, ID=id)
    engine.execute(insert_query)
    logging.info("New game data inserted!")

def delete_incorrect_game_data(sport, date, time, opponent, home_away, result, id):
    delete_query = db.delete(games).values(Sport=sport, Date=date, Time=time, Opponent=opponent, At=home_away, Result=result, ID=id)
    engine.execute(delete_query)
    logging.info("Incorrect game data deleted!")

def delete_old_game_data():
    #Delete old game data
    all_games = db.select([games])
    result = engine.execute(all_games).fetchall()
    for game in result:
        sport, date, time, opponent, home_away, result = game[0], game[1], game[2], game[3], game[4], game[5]
        if date != yesterday_date and date != current_date:
            delete_query = db.delete(games).where(db.and_(games.columns.Sport == sport, games.columns.Date == date, games.columns.Time == time, games.columns.Opponent == opponent, games.columns.At == home_away, games.columns.Result == result))
            engine.execute(delete_query)
            logging.info("Old game data deleted!")