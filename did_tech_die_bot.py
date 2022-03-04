from logging import raiseExceptions
import re
import tweepy
import constants
import did_tech_die_cfb

# Authenticate to Twitter
consumer_key=constants.twitter_consumer_key
consumer_secret=constants.twitter_consumer_secret
access_token=constants.twitter_access_token
access_token_secret=constants.twitter_access_token_secret
bearer_token=constants.twitter_bearer_token
client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key,consumer_secret=consumer_secret,
access_token=access_token,access_token_secret=access_token_secret)

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
                print("Checking if tweet already exists...")
                # Get CFB Game and Tweet data
                new_tweet = did_tech_die_cfb.get_resulting_tweet(cfb_game_data)
                print("New tweet:\n" + new_tweet + "\n")
                #Get bot's recent tweets
                recent_tweets = client.get_users_tweets(id=constants.twitter_user_id, user_auth=True).data
                #No recent tweets
                if recent_tweets != None:
                    for tweet in range(len(recent_tweets)):
                        print("Recent tweet " + str(tweet+1) + ":\n" + recent_tweets[tweet]["text"] + "\n")
                        if recent_tweets[tweet]["text"] == new_tweet:
                            print("Duplicate tweet exists! No tweets to create!")
                            return
                print("Creating tweet...")
                #Create tweet
                response = client.create_tweet(text=new_tweet)
                print("New tweet: " + f"https://twitter.com/user/status/{response.data['id']}")
                
                

create_cfb_tweet()
#Todo: check if cfb game is final on game days after some time interval 
#Todo: when game is final: tweet and stop checking if game is final until the next game week
#print(cfb_game_data)
#print(cfb_is_today_gameday)