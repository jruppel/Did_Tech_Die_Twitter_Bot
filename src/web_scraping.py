# Web Scraping
import re
from datetime import datetime
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import constants
import requests

HEADERS=constants.HEADERS
year=constants.year
two_days_ago_date=constants.two_days_ago_date
yesterday_date=constants.yesterday_date
current_date=constants.current_date
boxscore_sports=constants.boxscore_sports
logging=constants.logging
url=constants.url
"""
def get_website_data(sport_url,sport):
    df=pd.read_html(sport_url,header=0,extract_links='body')[0]
    for col in ['Date','Time','Opponent','At','Result','Links']:
        if col not in df.columns:
            logging.warning("{} does not exist on the {} sport grid. Skipping this sport.".format(col,sport_url))
            return 
    df['Date']=df['Date'].apply(lambda x:x[0] if isinstance(x,tuple) else x)
    df['Time']=df['Time'].apply(lambda x:x[0] if isinstance(x,tuple) else x)
    df['Opponent']=df['Opponent'].apply(lambda x:x[0] if isinstance(x,tuple) else x)
    df['At']=df['At'].apply(lambda x:x[0] if isinstance(x,tuple) else x)
    df['Result'] = df['Result'].apply(lambda x: x[0] if isinstance(x,tuple) else x)
    df['Links'] = df['Links'].apply(lambda x: x[1] if isinstance(x,tuple) else x)
    # Add game number column
    df.insert(0,'Game #',range(1,len(df)+1))
    # Handle the 'Tournament' column only if it's bowling
    if sport=="womens-bowling":
        if 'Tournament' in df.columns:  # Check if 'Tournament' column exists
            df['Tournament']=df['Tournament'].apply(lambda x:x[0] if isinstance(x,tuple) else x)
        df=df[['Game #','Date','Time','Opponent','At','Result','Links','Tournament']]
    else:
        df=df[['Game #','Date','Time','Opponent','At','Result','Links']]
        df['Tournament']=None
    # Filter for recent games
    tech_games=df[df.Date.isin([current_date, yesterday_date, two_days_ago_date])]
    if tech_games.empty:
        logging.info("Tech did not play recently in this sport!")
        return None
    # Convert to list
    games=tech_games.values.tolist()
    logging.info("Tech played recently in this sport!")
    logging.debug(games)
    return games
"""
def get_sport_schedules_url(sport_id):
    return (
        f"{url}/api/v2/Schedule/pasts?initialSportId={sport_id}&endSportId={sport_id}"
    )

def get_sport_schedules(sport_id):
    schedule_url=get_sport_schedules_url(sport_id)
    response=requests.get(schedule_url,headers=HEADERS)
    if response.status_code!=200:
        logging.warning(f"Failed to fetch schedule for sport ID {sport_id}. Status code: {response.status_code}")
        return None
    return response.json()

def get_sport_schedule_id(sport_id,sport_year):
    schedules=get_sport_schedules(sport_id)
    if not schedules:
        return None
    return next(
        (
            schedule["scheduleId"]
            for schedule in schedules
            if schedule["seasonTitle"]==str(sport_year)
        ),
        None
    )

def get_sport_schedule(sport_id,sport_year):
    schedule_id=get_sport_schedule_id(sport_id,sport_year)
    if schedule_id is None:
        logging.warning(f"No schedule found for sport ID {sport_id} and year {sport_year}.")
        return None
    schedule_url = f"{url}/api/v2/Schedule/{schedule_id}"
    response = requests.get(schedule_url,headers=HEADERS)
    if response.status_code != 200:
        logging.warning(f"Failed to fetch schedule for schedule ID {schedule_id}. Status code: {response.status_code}")
        return None
    return response.json()

def get_sport_schedule_games(sport_id,sport_year):
    schedule=get_sport_schedule(sport_id,sport_year)
    if schedule is None:
        return None
    return schedule["games"]

def get_sport_schedule_recent_games(sport_id,sport_year):
    games = get_sport_schedule_games(sport_id,sport_year)
    if games is None:
        return None
    recent_games = [
        game for game in games
        if datetime.fromisoformat(game["date"]).date() in {current_date,yesterday_date,two_days_ago_date}
    ]
    if not recent_games:
        logging.info("No recent games found for sport ID {}.".format(sport_id))
        return None
    logging.info("Found {} recent games for sport ID {}.".format(len(recent_games),sport_id))
    return recent_games


def get_results_data(sport_id, game_id):
    results_url = f"{url}/api/v2/ScheduleGames/{game_id}/results?sportId={sport_id}"
    response = requests.get(results_url, headers=HEADERS)
    if response.status_code != 200:
        logging.warning(f"Failed to fetch results for game ID {game_id}. Status code: {response.status_code}")
        return None
    return response.json()


def get_team_rankings(boxscore_matchup):
    team_ranking=""
    opponent_ranking=""
    if "#" in boxscore_matchup:
        re.search(r"#([^ ]*)",)

def get_valid_records(boxscore_team_record,boxscore_opponent_record):
    team_split_parts=boxscore_team_record.replace("(", "").replace(")", "").replace(" ,",",").replace(", ",",")
    opponent_split_parts=boxscore_opponent_record.replace("(", "").replace(")", "").replace(" ,",",").replace(", ",",")
    if team_split_parts.count(",")==1:
        team_record_comma_index=team_split_parts.find(',')
        if team_split_parts[:team_record_comma_index].find("-")==-1:
            team_split_parts=team_split_parts[team_record_comma_index+1:]
        else:
            team_split_parts=team_split_parts[:team_record_comma_index]
    elif team_split_parts.count(",")==2:
        first_team_record_comma_index=team_split_parts.find(',')
        second_team_record_comma_index=team_split_parts.find(',',team_split_parts.find(',')+1)
        team_split_parts=team_split_parts[first_team_record_comma_index+1:second_team_record_comma_index]
    if opponent_split_parts.count(",")==1:
        opponent_record_comma_index=opponent_split_parts.find(',')
        if opponent_split_parts[:opponent_record_comma_index].find("-")==-1:
            opponent_split_parts=opponent_split_parts[opponent_record_comma_index+1:]
        else:
            opponent_split_parts=opponent_split_parts[:opponent_record_comma_index]
    elif opponent_split_parts.count(",")==2:
        first_opponent_record_comma_index=opponent_split_parts.find(',')
        second_opponent_record_comma_index=opponent_split_parts.find(',',opponent_split_parts.find(',')+1)
        opponent_split_parts=opponent_split_parts[first_opponent_record_comma_index+1:second_opponent_record_comma_index]
    team_split_parts=team_split_parts.split('-')
    opponent_split_parts=opponent_split_parts.split('-')
    if len(team_split_parts)==3 and int(team_split_parts[-1])==0:
        team_split_parts.pop()
    if len(opponent_split_parts)==3 and int(opponent_split_parts[-1])==0:
        opponent_split_parts.pop()
    team_result=f"({'-'.join(team_split_parts)})"
    opponent_result=f"({'-'.join(opponent_split_parts)})"
    if team_result in {' ','()'}:
        team_result=''
    if opponent_result in {' ','()'}:
        opponent_result=''
    return team_result,opponent_result

def scrape_boxscore_records(boxscore_link):
    #Doing a catch-all try-except for now since some boxscore pages or team records may not exist 
    try:
        boxscore_page=requests.get("{}{}".format(url,boxscore_link)).text
        boxscore_soup=BeautifulSoup(boxscore_page,"html.parser")
        # Retreive the matchup info using the two () substrings on the boxscore page
        boxscore_matchup=re.search(r'.*(\(.*?\)).*(\(.*?\))',boxscore_soup.get_text()).group(0).replace('#', '').strip()
        logging.info("Boxscore matchup: {}".format(boxscore_matchup))
        boxscore_records=re.findall(r'(\(.*?\))',boxscore_matchup)
        logging.info("Boxscore record: {}".format(boxscore_records))
        # Retrieve team order from boxscore and split according
        if any(team in boxscore_matchup and boxscore_matchup.index(team)==0 for team in boxscore_teams):
            boxscore_team_record,boxscore_opponent_record=boxscore_records[0],boxscore_records[1]    
        else: 
            boxscore_team_record,boxscore_opponent_record=boxscore_records[1],boxscore_records[0]
        boxscore_team_record,boxscore_opponent_record=get_valid_records(boxscore_team_record,boxscore_opponent_record)
        logging.info("Team record: {} Opponent record: {}".format(boxscore_team_record,boxscore_opponent_record))
        return boxscore_team_record,boxscore_opponent_record
    except Exception as e:
        logging.warning("No boxscore found! Exception occured: {}!".format(e))
        return "",""
