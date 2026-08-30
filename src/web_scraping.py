# Web Scraping
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import constants

logging = constants.logging
url = constants.url

# Create a shared session with connection pooling and retry logic
session = requests.Session()
session.headers.update(constants.HEADERS)

retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
session.mount("https://", adapter)
session.mount("http://", adapter)

REQUEST_TIMEOUT = 10

def get_sport_schedules_url(sport_id: int) -> str:
    return f"{url}/api/v2/Schedule/pasts?initialSportId={sport_id}&endSportId={sport_id}"

def get_sport_schedules(sport_id: int):
    schedule_url = get_sport_schedules_url(sport_id)
    try:
        response = session.get(schedule_url, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch schedule for sport ID {sport_id}. Status code: {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        logging.warning(f"Error fetching schedules for sport ID {sport_id}: {e}")
        return None

def get_sport_schedule_id(sport_id: int, sport_year):
    schedules = get_sport_schedules(sport_id)
    if not schedules:
        return None
    return next(
        (
            schedule["scheduleId"]
            for schedule in schedules
            if schedule.get("seasonTitle") == str(sport_year)
        ),
        None
    )

def get_sport_schedule(sport_id: int, sport_year):
    schedule_id = get_sport_schedule_id(sport_id, sport_year)
    if schedule_id is None:
        logging.warning(f"No schedule found for sport ID {sport_id} and year {sport_year}.")
        return None
    schedule_url = f"{url}/api/v2/Schedule/{schedule_id}"
    try:
        response = session.get(schedule_url, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch schedule for schedule ID {schedule_id}. Status code: {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        logging.warning(f"Error fetching schedule for schedule ID {schedule_id}: {e}")
        return None

def get_sport_schedule_games(sport_id: int, sport_year):
    schedule = get_sport_schedule(sport_id, sport_year)
    if schedule is None:
        return None
    return schedule.get("games")

def get_sport_schedule_recent_games(sport_id: int, sport_year):
    games = get_sport_schedule_games(sport_id, sport_year)
    if games is None:
        return None
    recent_dates = {constants.current_date, constants.yesterday_date, constants.two_days_ago_date}
    recent_games = [
        game for game in games
        if game.get("date") and datetime.fromisoformat(game["date"]).date() in recent_dates
    ]
    if not recent_games:
        logging.info(f"No recent games found for sport ID {sport_id}.")
        return None
    logging.info(f"Found {len(recent_games)} recent games for sport ID {sport_id}.")
    return recent_games

def get_results_data(sport_id: int, game_id: str):
    results_url = f"{url}/api/v2/ScheduleGames/{game_id}/results?sportId={sport_id}"
    try:
        response = session.get(results_url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 204:
            logging.debug(f"No results posted yet for game ID {game_id} (HTTP 204).")
            return None
        if response.status_code != 200:
            logging.warning(f"Failed to fetch results for game ID {game_id}. Status code: {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        logging.warning(f"Error fetching results for game ID {game_id}: {e}")
        return None

