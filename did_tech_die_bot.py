from datetime import date, datetime
import random
import time as tm
import tweepy
import constants
import did_tech_die

# Authenticate to Twitter
consumer_key = constants.twitter_consumer_key
consumer_secret = constants.twitter_consumer_secret
access_token = constants.twitter_access_token
access_token_secret = constants.twitter_access_token_secret
bearer_token = constants.twitter_bearer_token
client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key,consumer_secret=consumer_secret,access_token=access_token,access_token_secret=access_token_secret)

#Todo: Refactor mass tweeting
Y = 2000 # dummy leap year to allow input X-02-29 (leap day)
seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
           ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
           ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
           ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
           ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]
winter_sports = {'football', 'mens-basketball', 'womens-basketball', 'baseball', 'softball', 'womens-tennis', 'womens-bowling', 'mens-golf', 'womens-track-and-field', 'mens-track-and-field'}
spring_sports = {'mens-basketball', 'womens-basketball', 'baseball', 'softball', 'womens-tennis', 'womens-bowling', 'mens-golf', 'womens-track-and-field', 'mens-track-and-field'}
summer_sports = {'football', 'womens-volleyball', 'womens-cross-country', 'mens-cross-country', 'mens-golf'}
autumn_sports = {'football', 'mens-basketball', 'womens-basketball', 'womens-volleyball', 'womens-tennis', 'womens-bowling', 'mens-golf'}

#Get season to only tweet sports that are in-season
def get_season():
    now = date.today()
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)

def create_sport_tweets(sport):
    delay = random.randint(3, 15)
    tm.sleep(delay)
    print("----------------------------------------------------------------------------------------")
    print("Checking for recent {} games...".format(sport))
    url = did_tech_die.get_tech_url(sport)
    games = did_tech_die.get_game_data(url, sport)
    if games is not None:
        for game in range(len(games)):
            sport, date, time, opponent, home_away, result = games[game][0], games[game][1], games[game][2], games[game][3], games[game][4], games[game][5]
            #Todo: assign each value of game for did_tech_die functions to reduce redundant code
            print("Checking if {} game {} is final...".format(sport, game+1))
            game_is_final = did_tech_die.is_game_final(result)
            if game_is_final:
                print("Checking if tweet is duplicated...")
                is_duplicate = did_tech_die.is_game_in_db(sport, date, time, opponent, home_away, result)
                if not is_duplicate:
                    print("Updating game data in game db...")
                    did_tech_die.update_game_data(sport, date, time, opponent, home_away, result)
                    new_tweet = did_tech_die.set_tweet(sport, opponent, home_away, result)
                    response = client.create_tweet(text=new_tweet)
                    url = f"https://twitter.com/user/status/{response.data['id']}"
                    print("New {} tweet: {}\n".format(sport, url))

#Mass tweeting based on season
def tweet_seasonal_sports():
    season = get_season()
    if season == 'winter':
        for sport in winter_sports:
            create_sport_tweets(sport)
    if season == 'spring':
        for sport in spring_sports:
            create_sport_tweets(sport)
    if season == "summer":
        for sport in summer_sports:
            create_sport_tweets(sport)
    if season == "autumn":
        for sport in autumn_sports:
            create_sport_tweets(sport)

tweet_seasonal_sports()