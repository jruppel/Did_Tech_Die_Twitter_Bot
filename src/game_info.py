# Game Info
from datetime import datetime
import re
import constants

logging = constants.logging

def is_game_exhibition(opponent: str) -> bool:
    if not opponent:
        return False
    is_ex = "exhibition" in opponent.lower()
    if is_ex:
        logging.info("This Tech game is an exhibition; no tweet needed!")
    else:
        logging.info("This Tech game is not an exhibition!")
    return is_ex

def is_game_final(result) -> bool:
    if result and result not in {'Canceled', 'Cancelled', 'Postponed', ''}:
        logging.info("This Tech game is final!")
        return True
    logging.info(f"This Tech game is not final!\nResult: {result}")
    return False

def get_overall_record(record: str) -> str:
    if not record:
        return ""
    # get only the overall record (before comma)
    record = record.split(",")[0].strip()
    # collapse multiple dashes into one
    record = re.sub(r"-+", "-", record)
    # ensure record string is wrapped in parentheses
    if not record.startswith("("):
        record = f"({record})"
    return record

def nan_time_to_time(time) -> str:
    if time is None or time != time:
        return "None"
    return str(time)

def extract_game_details(game: dict, sport: str, results_data: dict) -> dict | None:
    result = game.get("result") or {}
    opponent_name = game.get("opponent", {}).get("title", "")
    game_id = str(game["id"])
    game_date = str(datetime.fromisoformat(game["date"]).date())
    time = nan_time_to_time(game.get("time"))
    home_away = game.get("atVs", "")
    notes = result.get("postscoreInfo", "")

    win_loss = results_data.get("resultStatus", "")
    boxscore = results_data.get("boxscore")

    if boxscore is not None:
        home = boxscore.get("home", {})
        away = boxscore.get("away", {})
        home_id = home.get("id", "")
        home_name = home.get("name", "").lower()
        if home_id in constants.tech_ids or home_name in constants.tech_names:
            tech_team = home
            opponent_team = away
        else:
            tech_team = away
            opponent_team = home

        tech_score = str(tech_team.get("score", ""))
        opponent_score = str(opponent_team.get("score", ""))
        tech_record = get_overall_record(tech_team.get("record", ""))
        opponent_record = get_overall_record(opponent_team.get("record", ""))
    else:
        tech_record = ""
        opponent_record = ""
        tech_score = (
            result.get("teamScore")
            or result.get("postscoreInfo")
            or result.get("prescoreInfo")
            or ""
        )
        if not tech_score:
            return None
        opponent_score = str(result.get("opponentScore", ""))

        if sport in constants.TRACK_AND_FIELD_SPORTS:
            parts = [part.strip() for part in str(tech_score).split(";")]
            index = 0 if sport in {"mens-track-and-field", "mens-cross-country"} else 1
            if len(parts) > index and len(parts[index].split()) > 1:
                tech_score = parts[index].split()[1]

    return {
        "game_id": game_id,
        "sport": sport,
        "date": game_date,
        "time": time,
        "opponent": opponent_name,
        "home_away": home_away,
        "result_status": win_loss,
        "team_score": str(tech_score),
        "opponent_score": str(opponent_score),
        "team_record": tech_record,
        "opponent_record": opponent_record,
        "notes": notes
    }
