# Database
import constants
import sqlalchemy as db
from sqlalchemy import text
from datetime import datetime, timezone

logging = constants.logging

def utc_now():
    return datetime.now(timezone.utc)

class Database:
    def __init__(self, sql_db):
        self.engine = db.create_engine(sql_db)
        self.metadata = db.MetaData()
        self.games = db.Table(
              "games",
              self.metadata,
              db.Column("game_id", db.String, primary_key=True),
              db.Column("sport", db.String),
              db.Column("date", db.String),
              db.Column("time", db.String),
              db.Column("opponent", db.String),
              db.Column("home_away", db.String),
              db.Column("result_status", db.String),
              db.Column("team_record", db.String),
              db.Column("team_score", db.String),
              db.Column("opponent_record", db.String),
              db.Column("opponent_score", db.String),
              db.Column("notes", db.String),
              db.Column("post_text", db.String),
              db.Column("post_id", db.String, nullable=True),
              db.Column("posted_at", db.DateTime, default=utc_now),
              db.Column("last_updated_at", db.DateTime, default=utc_now),
              db.Column("correction_count", db.Integer, default=0)
)
        self.metadata.create_all(self.engine)
    def get_game_data(self, game_id):
        with self.engine.begin() as connection:
            return connection.execute(
                db.select(self.games)
                .where(self.games.columns.game_id == game_id)
            ).fetchone()
    def get_all_game_data(self):
        with self.engine.begin() as connection:
            return connection.execute(
                db.select(self.games)
            ).fetchall()
    def has_game(self, game_id):
        return self.get_game_data(game_id) is not None
    def has_game_changed(self, game_id, game):
        existing = self.get_game_data(game_id)

        if existing is None:
            return False

        fields = {
            "team_record": (existing.team_record, game["team_record"]),
            "team_score": (existing.team_score, game["team_score"]),
            "opponent_record": (existing.opponent_record, game["opponent_record"]),
            "opponent": (existing.opponent, game["opponent"]),
            "opponent_score": (existing.opponent_score, game["opponent_score"]),
            "home_away": (existing.home_away, game["home_away"]),
            "result_status": (existing.result_status, game["result_status"]),
            "notes": (existing.notes, game["notes"]),
        }
        changed = False

        for field, values in fields.items():
            if values[0] != values[1]:
                logging.info(
                    f"Game {game_id} changed: {field}: "
                    f"{values[0]!r} ({type(values[0])}) -> "
                    f"{values[1]!r} ({type(values[1])})"
                )
                changed = True

        return changed
    def insert_game(self, game):
        with self.engine.begin() as connection:
            connection.execute(
                db.insert(self.games).values(
                    game_id=game["game_id"],
                    sport=game["sport"],
                    date=game["date"],
                    time=game["time"],
                    opponent=game["opponent"],
                    home_away=game["home_away"],
                    result_status=game["result_status"],
                    team_record=game["team_record"],
                    team_score=game["team_score"],
                    opponent_record=game["opponent_record"],
                    opponent_score=game["opponent_score"],
                    notes=game["notes"],
                    post_id=game.get("post_id"),
                    post_text=game.get("post_text"),
                    last_updated_at=utc_now()
                )
            )
        logging.info(f"Inserted game {game['game_id']}")
    def update_game(self, game_id, **kwargs):
        kwargs["last_updated_at"] = utc_now()
        with self.engine.begin() as connection:
            connection.execute(
                db.update(self.games)
                .where(self.games.columns.game_id == game_id)
                .values(**kwargs)
            )
    def has_post(self, game_id):
        game = self.get_game_data(game_id)
        if game is None:
            return False
        return game.post_id is not None
    def mark_posted(self, game_id, post_id, post_text):
        with self.engine.begin() as connection:
            connection.execute(
                db.update(self.games)
                .where(self.games.columns.game_id == game_id)
                .values(
                    post_id=post_id,
                    post_text=post_text,
                    posted_at=utc_now(),
                    last_updated_at=utc_now()
                )
            )
        logging.info(f"Marked game {game_id} as posted")
    def clear_post(self, game_id):
        with self.engine.begin() as connection:
            connection.execute(
                db.update(self.games)
                .where(self.games.columns.game_id == game_id)
                .values(
                    post_id=None,
                    post_text=None,
                    last_updated_at=utc_now()
                )
            )
        logging.info(f"Cleared post for {game_id}")
    def get_unposted_games(self):
        with self.engine.begin() as connection:
            return connection.execute(
                db.select(self.games)
                .where(self.games.columns.post_id.is_(None))
            ).fetchall()
    def increment_correction_count(self, game_id):
        with self.engine.begin() as connection:
            connection.execute(
                db.update(self.games)
                .where(self.games.columns.game_id == game_id)
                .values(
                    correction_count=self.games.c.correction_count + 1,
                    last_updated_at=utc_now()
                )   
            )
        logging.info(f"Incremented correction count for {game_id}")