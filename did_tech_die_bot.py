import tweepy
import constants
import did_tech_die_cfb

# Authenticate to Twitter
consumer_key=constants.twitter_consumer_key
consumer_secret=constants.twitter_consumer_secret
access_token=constants.twitter_access_token
access_token_secret=constants.twitter_access_token_secret
client = tweepy.Client(consumer_key=consumer_key,consumer_secret=consumer_secret,
access_token=access_token,access_token_secret=access_token_secret)
# Todo: get today's date, get week # from date, check if today is football

def create_cfb_tweet(year, day, season_type):
    # Get CFB Game data
    cfb_game_data = did_tech_die_cfb.get_game_data(year, day, season_type)
    cfb_game_result = did_tech_die_cfb.get_result(cfb_game_data)
    #Create tweet
    if cfb_game_result == 'L':
        response = client.create_tweet(text='Yes')
    if cfb_game_result == 'W':
        response = client.create_tweet(text='No')
    print(response)
    #print(cfb_game_data)

#Todo: if total games is week #, create tweet