# Database
import constants
import sqlalchemy as db
from sqlalchemy import text

logging=constants.logging
two_days_ago_date=constants.two_days_ago_date
yesterday_date=constants.yesterday_date
current_date=constants.current_date

class Database:
    def __init__(self, sql_db):
        self.engine = db.create_engine(sql_db)
        self.metadata = db.MetaData()
        self.games = db.Table(
            "games",
            self.metadata,
            db.Column("game_num", db.Integer),
            db.Column("sport", db.String),
            db.Column("date", db.String),
            db.Column("time", db.String),
            db.Column("opponent", db.String),
            db.Column("at", db.String),
            db.Column("result", db.String),
            db.Column("team_record", db.String),
            db.Column("opponent_record", db.String),
            db.Column("id", db.String)
        )
        self.metadata.create_all(self.engine)
    def is_game_in_db(self,game_num,sport,date,time,opponent,home_away,team_record,opponent_record,result):
        existing_games=self.get_game_data(game_num,sport,date,time,opponent,home_away,result,team_record,opponent_record,None)
        if not existing_games:
            logging.info("Tweet is not a duplicate!")
            return False
        logging.info("Tech played recently in this sport, but it was already tweeted!")
        return True
    def get_game_data(self,game_num,sport,date,time,opponent,at,result,team_record,opponent_record,id):
        conditions_list=[getattr(self.games.columns,col)==value for col,value in locals().items() if value is not None and col != "self"]
        with self.engine.begin() as connection:
            return connection.execute(
                db.select(self.games)
                .where(db.and_(*conditions_list))
            ).fetchall()
    def get_all_game_data(self):
        with self.engine.begin() as connection:
            return connection.execute(
                db.select(self.games)
            ).fetchall()
    def insert_new_game_data(self,gd_game_num,gd_sport,gd_date,gd_time,gd_opponent,gd_at,gd_result,gd_team_record,gd_opponent_record,gd_id):
        with self.engine.begin() as connection:
            connection.execute(
                db.insert(self.games).values(
                    game_num=gd_game_num,
                    sport=gd_sport,
                    date=gd_date,
                    time=gd_time,
                    opponent=gd_opponent,
                    at=gd_at,
                    result=gd_result,
                    team_record=gd_team_record,
                    opponent_record=gd_opponent_record,
                    id=gd_id
                )
            )
        logging.info("New game data inserted!")
    def delete_incorrect_game_data(self,gd_id):
        with self.engine.begin() as connection:
            connection.execute(db.delete(self.games).where(self.games.columns.id==gd_id))
        logging.info("Incorrect game data deleted!")
    def delete_old_game_data(self):
        #Delete old game data
        with self.engine.begin() as connection:
            connection.execute(
        text("""
            DELETE FROM games
            WHERE date NOT IN (:date1, :date2, :date3)
            """),
        {
            "date1": two_days_ago_date,
            "date2": yesterday_date,
            "date3": current_date
        }
    )