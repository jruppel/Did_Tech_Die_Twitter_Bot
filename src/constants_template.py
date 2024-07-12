from datetime import datetime, date, timedelta
import logging
import tweepy
import time as tm
import random
import os

testing=True

#File path info
if os.name == "nt":
    path=""
else:
    path=""

#DB info
sql_db="sqlite:///{}gamedata.db".format(path)

# Logging info
log='{}bot.log'.format(path)
logging.basicConfig(
     filename=log,
     level=logging.DEBUG, 
     format= '[%(asctime)s] {%(module)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%m-%d-%Y %H:%M:%S'
 )

#Main Twitter API
main_credentials={
'consumer_key':'',
'consumer_secret':'',
'access_token':'',
'access_token_secret':'',
'bearer_token':''
}

#Testing Twitter API
testing_credentials={
'consumer_key':'',
'consumer_secret':'',
'access_token':'',
'access_token_secret':'',
'bearer_token':''
}

# Twiter Authentication
# Set testing account constants
if testing:
    credentials=testing_credentials
# Set main account constants
else:
    credentials=main_credentials

client=tweepy.Client(bearer_token=credentials['bearer_token'],consumer_key=credentials['consumer_key'],
                    consumer_secret=credentials['consumer_secret'],access_token=credentials['access_token'],
                    access_token_secret=credentials['access_token_secret'],wait_on_rate_limit=True)

# Tweet delay
delay=tm.sleep(random.randint(3, 15))

#Gmail info for texting
smtp_provider=""
recipient=""
email=""
password=""

# Date/time info
today=date.today()
yesterday=today-timedelta(days=1)
year=today.year
last_year=year-1
next_year=year+1
current_date=today.strftime('%B X%d, %Y (%A)').replace('X0','X').replace('X','')
yesterday_date=yesterday.strftime('%B X%d, %Y (%A)').replace('X0','X').replace('X','')
current_time=datetime.now().strftime('%H:%M')
if date(year,1,1)<=today<=date(year,6,20):
    biannual_year="{}-{}".format(str(last_year),str(year)[2:])
if date(year,6,21)<=today<=date(year,12,31):
    biannual_year="{}-{}".format(str(year),str(next_year)[2:])

# Season info
Y=2000 # dummy leap year to allow input X-02-29 (leap day)
seasons=[('winter',(date(Y,1,1),date(Y,3,20))),
    ('spring',(date(Y,3,21),date(Y,6,20))),
    ('summer',(date(Y,6,21),date(Y,9,22))),
    ('autumn',(date(Y,9,23),date(Y,12,20))),
    ('winter',(date(Y,12,21),date(Y,12,31)))]
now=today.replace(year=Y)
season=next(season for season,(start,end) in seasons if start<=now<=end)

# Sport info
tweet_team=""
#boxscore_teams={"", "", "", "", "", ""}
url=""
sports={
    "football":{
        "emoji":"🏈",
        "season":["summer","autumn","winter"],
        "boxscore":True,
        "url":"{}/sports/football/schedule/{}?grid=true".format(url,year),       
        },
    "mens-basketball":{
        "emoji":"Men's 🏀",
        "season":["autumn","winter","spring"],
        "boxscore":True,
        "url":"{}/sports/mens-basketball/schedule/{}?grid=true".format(url,biannual_year)
        },
    "womens-basketball":{
        "emoji":"Women's 🏀",
        "season":["autumn","winter","spring"],
        "boxscore":True,
        "url":"{}/sports/womens-basketball/schedule/{}?grid=true".format(url,biannual_year)
        },
    "baseball":{
        "emoji":"⚾",
        "season":["winter","spring","summer"],
        "boxscore":True,
        "url":"{}/sports/baseball/schedule/{}?grid=true".format(url,year)
        },
    "softball":{
        "emoji":"🥎",
        "season":["winter","spring"],
        "boxscore":True,
        "url":"{}/sports/softball/schedule/{}?grid=true".format(url,biannual_year)
        },
    "womens-soccer":{
        "emoji":"⚽",
        "season":["summer","autumn"],
        "boxscore":True,
        "url":"{}/sports/womens-soccer/schedule/{}?grid=true".format(url,year)
        },
    "womens-volleyball":{
        "emoji":"🏐",
        "season":["summer","autumn"],
        "boxscore":True,
        "url":"{}/sports/womens-volleyball/schedule/{}?grid=true".format(url,year)
        },
    "womens-tennis":{
        "emoji":"🎾",
        "season":["autumn","winter","spring"],
        "boxscore":True,
        "url":"{}/sports/womens-tennis/schedule/{}?grid=true".format(url,biannual_year)
        },
    "womens-bowling":{
        "emoji":"🎳",
        "season":["autumn","winter","spring"],
        "boxscore":False,
        "url":"{}/sports/womens-bowling/schedule/{}?grid=true".format(url,biannual_year)
    },
    "mens-golf":{
        "emoji":"⛳",
        "season":["autumn","winter","spring"],
        "boxscore":False,
        "url":"{}/sports/mens-golf/schedule/{}?grid=true".format(url,biannual_year)
    },
    "mens-track-and-field":{
        "emoji":"Men's T&F 🏃",
        "season":["winter","spring"],
        "boxscore":False,
        "url":"{}/sports/track-and-field/schedule/{}?grid=true".format(url,year)
    },
    "womens-track-and-field":{
        "emoji":"Women's T&F 🏃",
        "season":["winter","spring"],
        "boxscore":False,
        "url":"{}/sports/track-and-field/schedule/{}?grid=true".format(url,year)
    },
    "mens-cross-country":{
        "emoji":"Men's XC 🏃",
        "season":["summer","autumn"],
        "boxscore":False,
        "url":"{}/sports/cross-country/schedule/{}?grid=true".format(url,year)
    },
    "womens-cross-country":{
        "emoji":"Women's XC 🏃",
        "season":["summer","autumn"],
        "boxscore":False,
        "url":"{}/sports/cross-country/schedule/{}?grid=true".format(url,year)
    }
}
seasonal_sports={sport:info for sport,info in sports.items() if season in info["season"]}
boxscore_sports={sport for sport,info in seasonal_sports.items() if info["boxscore"] is True}
no_boxscore_sports={sport for sport,info in seasonal_sports.items() if info["boxscore"] is False}

