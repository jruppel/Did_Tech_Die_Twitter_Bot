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

cfb_game_week = did_tech_die_cfb.get_game_week()
cfb_game_data = did_tech_die_cfb.get_game_data(cfb_game_week[0], cfb_game_week[1])
cfb_gameday = did_tech_die_cfb.today_is_football()
cfb_tweets = cfb_game_week[0] - 1

def create_cfb_tweet():
    # Get CFB Game data
    print("Checking if game is final.")
    cfb_game_is_final = did_tech_die_cfb.game_is_final()
    tweets = cfb_tweets
    if cfb_game_is_final and cfb_gameday and tweets != cfb_game_week[0]:
        cfb_game_result = did_tech_die_cfb.get_result(cfb_game_data)
        print("Crafting tweet.")
        #Create tweet
        #Todo: include sport, teams, and score in tweet
        if cfb_game_result == 'L':
            response = client.create_tweet(text='Yes')
        if cfb_game_result == 'W':
            response = client.create_tweet(text='No')
        cfb_tweets = cfb_tweets + 1
    print(response)

print(cfb_tweets)
create_cfb_tweet()
print(cfb_tweets)
#Todo: check if cfb game is final on game days after some time interval 
#Todo: when game is final: tweet and stop checking if game is final until the next game week