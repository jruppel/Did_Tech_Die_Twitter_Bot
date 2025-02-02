# Web Scraping
import re
from datetime import date
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import constants
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

year,last_year,next_year,today,yesterday_date,two_days_ago_date,current_date,url,boxscore_teams,logging=constants.year,constants.last_year,constants.next_year,constants.today,constants.yesterday_date,constants.two_days_ago_date,constants.current_date,constants.url,constants.boxscore_teams,constants.logging

def get_sport_url(sport):
    if sport in {'mens-basketball','womens-basketball','womens-tennis','womens-bowling','mens-golf'}:
        if date(year,1,1)<=today<=date(year,6,20):
            url_year=str(last_year)+"-"+str(year)[2:]
        if date(year,6,21)<=today<=date(year,12,31):    
            url_year=str(year)+"-"+str(next_year)[2:]
    if sport in {'baseball','womens-soccer','softball','womens-volleyball','football','womens-cross-country',
                 'mens-cross-country','womens-track-and-field','mens-track-and-field'}:
        url_year=year
        if sport in {'womens-cross-country','mens-cross-country','womens-track-and-field','mens-track-and-field'}:
            sport=sport.split("-", 1)[1]
    sport_url='{}/sports/{}/schedule/{}?grid=true'.format(url,sport,url_year)
    return sport_url

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
