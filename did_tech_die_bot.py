from cgitb import reset
from datetime import date, datetime
from urllib import response
import tweepy
import constants
import did_tech_die_cfb
import did_tech_die_mbb

# Authenticate to Twitter
consumer_key=constants.twitter_consumer_key
consumer_secret=constants.twitter_consumer_secret
access_token=constants.twitter_access_token
access_token_secret=constants.twitter_access_token_secret
bearer_token=constants.twitter_bearer_token
client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key,consumer_secret=consumer_secret,
access_token=access_token,access_token_secret=access_token_secret)
recent_tweets = client.get_users_tweets(id=constants.twitter_user_id, user_auth=True).data
Y = 2000 # dummy leap year to allow input X-02-29 (leap day)
seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
           ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
           ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
           ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
           ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]

#Get season to only tweet sports that are in-season
def get_season():
    now = date.today()
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)

#Check for tweet duplication before tweeting
def is_tweet_duplicate(new_tweet):
    print("Checking if tweet already exists...")
    if recent_tweets != None:
        for tweet in range(len(recent_tweets)):
            if recent_tweets[tweet]["text"] == new_tweet:
                print("Duplicate tweet exists! No tweets to create!\n")
                return True
    print("Tweet does not exist!\n")
    return False

#Tech college football tweets
def create_cfb_tweet():
    cfb_game_week = did_tech_die_cfb.get_game_week()
    #Checking if this week is a game week
    if cfb_game_week is not None:
        cfb_game_data = did_tech_die_cfb.get_game_data(cfb_game_week[0], cfb_game_week[1])
        cfb_is_today_gameday = did_tech_die_cfb.is_today_gameday(cfb_game_data)
        #Checking if game day is today
        if cfb_is_today_gameday:
            cfb_game_is_final = did_tech_die_cfb.is_game_final(cfb_game_data)
            #Checking if final score is posted
            if cfb_game_is_final:
                # Get CFB Game and Tweet data
                new_tweet = did_tech_die_cfb.get_resulting_tweet(cfb_game_data)
                is_duplicate = is_tweet_duplicate(new_tweet)
                #No recent tweets
                if is_duplicate == False:
                    print("Creating CFB tweet...")
                    #Create tweet
                    response = client.create_tweet(text=new_tweet)
                    print("New CFB tweet: " + f"https://twitter.com/user/status/{response.data['id']}")

#Tech men's basketball tweets
def create_mbb_tweet():
    mbb_game_today = did_tech_die_mbb.get_game_data()
    if mbb_game_today is not None:
        mbb_game_is_final = did_tech_die_mbb.is_game_final(mbb_game_today)
        if mbb_game_is_final:
            new_tweet = did_tech_die_mbb.get_resulting_tweet(mbb_game_today)
            is_duplicate = is_tweet_duplicate(new_tweet)
            if is_duplicate == False:
                print("New MBB tweet: " + f"https://twitter.com/user/status/{response.data['id']}")

#Mass tweeting based on season
def create_tweets():
    season = get_season()
    if season == 'winter':
        create_cfb_tweet()
        create_mbb_tweet()
    if season == 'spring':
        create_mbb_tweet()
    if season == "summer":
        create_cfb_tweet()
    if season == "autumn":
        create_cfb_tweet()
        create_mbb_tweet()


create_tweets()