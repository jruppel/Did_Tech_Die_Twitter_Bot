# Web Scraping
import re
from datetime import date
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import constants

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

def get_website_data(url, sport):
    try:
        df=pd.read_html(url, header=0)[0]
        recent_games=df[df.Date.isin([current_date,yesterday_date])].where(pd.notnull(df),None)
    except AttributeError:
        logging.warning("Current year schedule for this sport has not been created yet!")
        return
    else:
        if recent_games.empty:
            logging.info("Tech did not play recently in this sport!")
            return   
        tech_games=recent_games[~recent_games.Opponent.str.contains("vs.")]
        game_info=tech_games[['Date', 'Time', 'Opponent', 'At', 'Result']]
        game_info.insert(0, 'Sport', sport.capitalize())
        games=game_info.values.tolist()
        logging.info("Tech played recently in this sport!")
        logging.debug(games)
        return games
    
def get_boxscore_records(sport_url,opponent):
    sport_page=urllib.request.urlopen(sport_url)
    sport_soup=BeautifulSoup(sport_page,"html.parser")
    # Retrieve the last a tag which has the text Box Score's href attribute value
    href_link=sport_soup.find_all('a',text='Box Score')[-1]['href']
    boxscore_page = urllib.request.urlopen("{}{}".format(url,href_link))
    boxscore_soup = BeautifulSoup(boxscore_page,"html.parser")
    # Retrieve the text for the h2 tag with the team names and records
    try:
        boxscore_matchup = boxscore_soup.find('h2',{'class':'hide text-center text-uppercase hide-on-medium-down'}).text
    except AttributeError:
        logging.warning("Matchup not found on boxscore page! No records will be added to tweet!")
        return "",""
    logging.info("Boxscore matchup: {}".format(boxscore_matchup))
    try:
        boxscore_team_split = boxscore_matchup.split(team)[1].lstrip()
    except IndexError:
        boxscore_team_split = boxscore_matchup.split(team_abbr)[1].lstrip()
    boxscore_team_record = re.findall(f'[^{")"}]+\)?', boxscore_team_split)[0]
    boxscore_opponent_split = boxscore_matchup.split(opponent)[1].lstrip()
    boxscore_opponent_record = re.findall(f'[^{")"}]+\)?', boxscore_opponent_split)[0]
    return boxscore_team_record,boxscore_opponent_record