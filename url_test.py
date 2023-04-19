import re
from bs4 import BeautifulSoup
import urllib.request
from ast import Delete
from datetime import date
from datetime import timedelta
from distutils.log import debug
import pandas as pd
import sqlite3
import sqlalchemy as db
import constants
import logging

sport = "baseball"
href_sport = str.capitalize(sport)
opponent = "FIU"
team = "Louisiana Tech"
today = date.today()
yesterday = today - timedelta(days = 1)
year = today.year
last_year = year - 1
next_year = year + 1
current_date = today.strftime('%B X%d, %Y').replace('X0','X').replace('X','')
yesterday_date = yesterday.strftime('%B X%d, %Y').replace('X0','X').replace('X','')
yesterday_date = "April 16, 2023"

sport_page = urllib.request.urlopen("https://latechsports.com/sports/{}/schedule/{}?grid=true".format(sport,year))
sport_soup = BeautifulSoup(sport_page, "html.parser")
href_link = sport_soup.find('a', {'aria-label':'Box score of {} vs {} on {} at 11 AM'.format(href_sport,opponent,yesterday_date)})['href']

boxscore_page = urllib.request.urlopen("https://latechsports.com{}".format(href_link))
boxscore_soup = BeautifulSoup(boxscore_page, "html.parser")
boxscore_matchup = boxscore_soup.find('h2', {'class':'hide text-center text-uppercase hide-on-medium-down'}).text

boxscore_oppo_split = boxscore_matchup.split(opponent)[1].lstrip()
boxscore_oppo_record_split = re.findall(f'[^{")"}]+\)?', boxscore_oppo_split)[0]

boxscore_team_split = boxscore_matchup.split(team)[1].lstrip()
boxscore_team_record_split = re.findall(f'[^{")"}]+\)?', boxscore_team_split)[0]

