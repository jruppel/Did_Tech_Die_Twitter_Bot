# Game Info
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