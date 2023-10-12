# Web Scraping
import re
from datetime import date
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import constants
import requests

year,last_year,next_year,today,yesterday_date,current_date,url,team,team_abbr,logging=constants.year,constants.last_year,constants.next_year,constants.today,constants.yesterday_date,constants.current_date,constants.url,constants.team,constants.team_abbr,constants.logging

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
    try:
        df=pd.read_html(sport_url,header=0,extract_links='body')[0]
        df['Date']=df['Date'].apply(lambda x:x[0])
        df['Time']=df['Time'].apply(lambda x:x[0])
        df['Opponent']=df['Opponent'].apply(lambda x:x[0])
        df['At']=df['At'].apply(lambda x:x[0])
        df['Result']=df['Result'].apply(lambda x:x[0])
        df['Links']=df['Links'].apply(lambda x:x[1])
        tech_games=df[df.Date.isin([current_date,yesterday_date])]
    except AttributeError:
        logging.warning("Current year schedule for this sport has not been created yet!")
        return 
    else:
        if tech_games.empty:
            logging.info("Tech did not play recently in this sport!")
            return None
        game_info=tech_games[['Date','Time','Opponent','At','Result', 'Links']]
        game_info.insert(0,'Sport',sport)
        games=game_info.values.tolist()
        logging.info("Tech played recently in this sport!")
        logging.debug(games)
        return games

def get_team_rankings(boxscore_matchup):
    team_ranking=""
    opponent_ranking=""
    if "#" in boxscore_matchup:
        re.search(r"#([^ ]*)",)

def remove_conference_and_no_ties_records(boxscore_team_record,boxscore_opponent_record):
    team_split_parts=boxscore_team_record.replace("(", "").replace(")", "").replace(" ,",",")
    opponent_split_parts=boxscore_opponent_record.replace("(", "").replace(")", "").replace(" ,",",")
    team_record_comma_index=team_split_parts.find(',')
    opponent_record_comma_index=opponent_split_parts.find(',')
    if team_record_comma_index != -1:
        team_split_parts=team_split_parts[:team_record_comma_index]
    if opponent_record_comma_index != -1:
        opponent_split_parts=opponent_split_parts[:opponent_record_comma_index]
    team_split_parts=team_split_parts.split('-')
    opponent_split_parts=opponent_split_parts.split('-')
    if len(team_split_parts)==3 and int(team_split_parts[-1])==0:
        team_split_parts.pop()
    if len(opponent_split_parts)==3 and int(opponent_split_parts[-1])==0:
        opponent_split_parts.pop()
    team_result=f"({'-'.join(team_split_parts)})"
    opponent_result=f"({'-'.join(opponent_split_parts)})"
    return team_result,opponent_result

def scrape_boxscore_records(boxscore_link):
    #Doing a catch-all try-except for now since some boxscore pages or team records may not exist 
    try:
        boxscore_page=requests.get("{}{}".format(url,boxscore_link)).text
        boxscore_soup=BeautifulSoup(boxscore_page,"html.parser")
        # Retreive the matchup info using the two () substrings on the boxscore page
        boxscore_matchup=re.search(r'.*(\(.*?\)).*(\(.*?\))',boxscore_soup.get_text()).group(0).replace('#', '').strip()
        boxscore_records=re.findall(r'(\(.*?\))',boxscore_matchup)
        logging.info("Boxscore matchup: {}".format(boxscore_matchup))
        # Retrieve team order from boxscore and split according
        if (team in boxscore_matchup and boxscore_matchup.index(team)==0) or (team_abbr in boxscore_matchup and boxscore_matchup.index(team_abbr)==0):
            boxscore_team_record,boxscore_opponent_record=boxscore_records[0],boxscore_records[1]    
        else: 
            boxscore_team_record,boxscore_opponent_record=boxscore_records[1],boxscore_records[0]
        boxscore_team_record,boxscore_opponent_record=remove_conference_and_no_ties_records(boxscore_team_record,boxscore_opponent_record)
        logging.info("Team record: {} Opponent record: {}".format(boxscore_team_record,boxscore_opponent_record))
        return boxscore_team_record,boxscore_opponent_record
    except Exception as e:
        logging.warning("No boxscore found! Exception occured: {}!".format(e))
        return None,None