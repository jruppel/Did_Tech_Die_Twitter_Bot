# Manage DB
import constants
import sqlalchemy as db

sql_db,logging,two_days_ago_date,yesterday_date,current_date=constants.sql_db,constants.logging,constants.two_days_ago_date,constants.yesterday_date,constants.current_date

engine=db.create_engine(sql_db)
connection=engine.connect()
metadata=db.MetaData(engine)
if not db.inspect(engine).has_table('games'):
    db.Table('games',metadata,
          db.Column('game_num',db.Integer),
          db.Column('sport',db.String), 
          db.Column('date',db.String), 
          db.Column('time',db.String),
          db.Column('opponent',db.String), 
          db.Column('at',db.String),
          db.Column('result',db.String),
          db.Column('team_record',db.String),
          db.Column('opponent_record',db.String),
          db.Column('id',db.String)
    )
    metadata.create_all()
games = db.Table('games', metadata, autoload=True, autoload_with=engine)

def is_game_in_db(game_num,sport,date,time,opponent,home_away,team_record,opponent_record,result):
    result=get_game_data(game_num,sport,date,time,opponent,home_away,result,team_record,opponent_record,None)
    if not result:
        logging.info("Tweet is not a duplicate!")
        return False
    logging.info("Tech played recently in this sport, but it was already tweeted!")
    return True

def get_game_data(game_num,sport,date,time,opponent,at,result,team_record,opponent_record,id):
    conditions_list=[getattr(games.columns,col)==value for col,value in locals().items() if value is not None]
    all_games=engine.execute(db.select([games]).where(db.and_(*conditions_list))).fetchall()
    return all_games
    
def get_all_game_data():
    return engine.execute(db.select([games])).fetchall()

def insert_new_game_data(gd_game_num,gd_sport,gd_date,gd_time,gd_opponent,gd_at,gd_result,gd_team_record,gd_opponent_record,gd_id):
    #Insert new game data
    engine.execute(db.insert(games).values(game_num=gd_game_num,sport=gd_sport,date=gd_date,time=gd_time,opponent=gd_opponent,at=gd_at,result=gd_result,team_record=gd_team_record,opponent_record=gd_opponent_record,id=gd_id))
    logging.info("New game data inserted!")

def delete_incorrect_game_data(gd_id):
    engine.execute(db.delete(games).where(games.columns.id==gd_id))
    logging.info("Incorrect game data deleted!")

def delete_old_game_data():
    #Delete old game data
    engine.execute('''DELETE FROM games WHERE date NOT IN ('{}','{}','{}')'''.format(two_days_ago_date,yesterday_date,current_date))