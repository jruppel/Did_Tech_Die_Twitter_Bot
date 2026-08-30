from datetime import date, timedelta
import logging
import os
import tweepy

testing = os.getenv("DID_TECH_DIE_TESTING", "false").lower() == "true"

# DB info: in test mode uses local sqlite, in production reads NEON_DATABASE_URL
sql_db = "sqlite:///gamedata.db" if testing else os.environ.get("NEON_DATABASE_URL", "")

# Logging info
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(module)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m-%d-%Y %H:%M:%S'
)

# Main Twitter API
credentials = {
    'consumer_key': os.environ.get("X_CONSUMER_KEY", ""),
    'consumer_secret': os.environ.get("X_CONSUMER_SECRET", ""),
    'access_token': os.environ.get("X_ACCESS_TOKEN", ""),
    'access_token_secret': os.environ.get("X_ACCESS_TOKEN_SECRET", ""),
    'bearer_token': os.environ.get("X_BEARER_TOKEN", "")
}

client = tweepy.Client(
    bearer_token=credentials['bearer_token'],
    consumer_key=credentials['consumer_key'],
    consumer_secret=credentials['consumer_secret'],
    access_token=credentials['access_token'],
    access_token_secret=credentials['access_token_secret'],
    wait_on_rate_limit=True
)

# Ntfy info for alerts
ntfy_url = "https://ntfy.sh/"
ntfy_tweet_alerts_topic = "did_tech_die_tweets"

# Headers for requests
HEADERS = {
    "tenant": "latech",
    "User-Agent": "DidTechDieBot/1.0"
}

# Date/time info
current_date = date.today()
yesterday_date = current_date - timedelta(days=1)
two_days_ago_date = current_date - timedelta(days=2)
year = current_date.year
last_year = year - 1
next_year = year + 1

if current_date <= date(year, 6, 20):
    biannual_year = f"{last_year}-{str(year)[2:]}"
else:
    biannual_year = f"{year}-{str(next_year)[2:]}"

# Season info
Y = 2000  # dummy leap year to allow input X-02-29 (leap day)
seasons = [
    ('winter', (date(Y, 1, 1), date(Y, 3, 20))),
    ('spring', (date(Y, 3, 21), date(Y, 6, 20))),
    ('summer', (date(Y, 6, 21), date(Y, 9, 22))),
    ('autumn', (date(Y, 9, 23), date(Y, 12, 20))),
    ('winter', (date(Y, 12, 21), date(Y, 12, 31)))
]
now = current_date.replace(year=Y)
season = next(s for s, (start, end) in seasons if start <= now <= end)
# Sport info
tweet_team="Louisiana Tech"
tech_ids = {"LTU", "LATech", "TECH"}
tech_names={"Louisiana Tech","LA Tech","TECH","LA TECH","LOUISIANA TECH","LATECH"}
url="https://latechsports.com"
sports={
    "football":{
        "emoji":"🏈",
        "season":["summer","autumn","winter"],
        "boxscore":True,
        "sport_id":2,
        "year":year
        },
    "mens-basketball":{
        "emoji":"Men's 🏀",
        "season":["autumn","winter","spring"],
        "boxscore":True,
        "sport_id":5,
        "year":biannual_year
        },
    "womens-basketball":{
        "emoji":"Women's 🏀",
        "season":["autumn","winter","spring"],
        "boxscore":True,
        "sport_id":10,
        "year":biannual_year
        },
    "baseball":{
        "emoji":"⚾",
        "season":["winter","spring","summer"],
        "boxscore":True,
        "sport_id":1,
        "year":year
        },
    "softball":{
        "emoji":"🥎",
        "season":["winter","spring"],
        "boxscore":True,
        "sport_id":9,
        "year":year
        },
    "womens-soccer":{
        "emoji":"⚽",
        "season":["summer","autumn"],
        "boxscore":True,
        "sport_id":13,
        "year":year
        },
    "womens-volleyball":{
        "emoji":"🏐",
        "season":["summer","autumn"],
        "boxscore":True,
        "sport_id":16,
        "year":year
        },
    "womens-tennis":{
        "emoji":"🎾",
        "season":["autumn","winter","spring"],
        "boxscore":True,
        "sport_id":14,
        "year":biannual_year
        },
    "womens-bowling":{
        "emoji":"🎳",
        "season":["autumn","winter","spring"],
        "boxscore":False,
        "sport_id":11,
        "year":biannual_year
    },
    "mens-golf":{
        "emoji":"⛳",
        "season":["autumn","winter","spring"],
        "boxscore":False,
        "sport_id":7,
        "year":biannual_year
    },
    "mens-track-and-field":{
        "emoji":"Men's T&F 🏃",
        "season":["winter","spring"],
        "boxscore":False,
        "sport_id":20,
        "year":year
    },
    "womens-track-and-field":{
        "emoji":"Women's T&F 🏃",
        "season":["winter","spring"],
        "boxscore":False,
        "sport_id":20,
        "year":year
    },
    "mens-cross-country":{
        "emoji":"Men's XC 🏃",
        "season":["summer","autumn"],
        "boxscore":False,
        "sport_id":19,
        "year":year
    },
    "womens-cross-country":{
        "emoji":"Women's XC 🏃",
        "season":["summer","autumn"],
        "boxscore":False,
        "sport_id":19,
        "year":year
    }
}

TRACK_AND_FIELD_SPORTS = {
    "mens-track-and-field",
    "womens-track-and-field",
    "mens-cross-country",
    "womens-cross-country",
}

seasonal_sports={sport:info for sport,info in sports.items() if season in info["season"]}
boxscore_sports={sport for sport,info in seasonal_sports.items() if info["boxscore"] is True}
no_boxscore_sports={sport for sport,info in seasonal_sports.items() if info["boxscore"] is False}