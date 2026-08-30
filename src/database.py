# Database
from datetime import datetime, timezone
import sqlalchemy as db
import constants

logging = constants.logging

def utc_now():
    return datetime.now(timezone.utc)

class Database:
    def __init__(self, sql_db):
        self.engine = db.create_engine(sql_db, pool_pre_ping=True)
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
                .where(self.games.columns.game_id == str(game_id))
            ).fetchone()

    def has_game_changed(self, existing, game):
        if existing is None:
            return False

        # If a game_id was passed instead of an existing record, fetch it
        if isinstance(existing, (str, int)):
            existing = self.get_game_data(str(existing))
            if existing is None:
                return False

        game_id = existing.game_id
        fields = {
            "team_record": (existing.team_record or "", game["team_record"] or ""),
            "team_score": (str(existing.team_score or ""), str(game["team_score"] or "")),
            "opponent_record": (existing.opponent_record or "", game["opponent_record"] or ""),
            "opponent": (existing.opponent or "", game["opponent"] or ""),
            "opponent_score": (str(existing.opponent_score or ""), str(game["opponent_score"] or "")),
            "home_away": (existing.home_away or "", game["home_away"] or ""),
            "result_status": (existing.result_status or "", game["result_status"] or ""),
            "notes": (existing.notes or "", game["notes"] or ""),
        }
        changed = False

        for field, values in fields.items():
            if values[0] != values[1]:
                logging.info(
                    f"Game {game_id} changed: {field}: "
                    f"{values[0]!r} -> {values[1]!r}"
                )
                changed = True

        return changed

    def insert_game(self, game):
        with self.engine.begin() as connection:
            connection.execute(
                db.insert(self.games).values(
                    game_id=str(game["game_id"]),
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
                .where(self.games.columns.game_id == str(game_id))
                .values(**kwargs)
            )

    def mark_posted(self, game_id, post_id, post_text):
        with self.engine.begin() as connection:
            connection.execute(
                db.update(self.games)
                .where(self.games.columns.game_id == str(game_id))
                .values(
                    post_id=str(post_id) if post_id else None,
                    post_text=post_text,
                    posted_at=utc_now(),
                    last_updated_at=utc_now()
                )
            )
        logging.info(f"Marked game {game_id} as posted")

    def increment_correction_count(self, game_id):
        with self.engine.begin() as connection:
            connection.execute(
                db.update(self.games)
                .where(self.games.columns.game_id == str(game_id))
                .values(
                    correction_count=self.games.c.correction_count + 1,
                    last_updated_at=utc_now()
                )   
            )
        logging.info(f"Incremented correction count for {game_id}")