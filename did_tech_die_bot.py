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
            cfb_game_is_final = did_tech_die_cfb.game_is_final(cfb_game_data)
            #Checking if final score is posted
            if cfb_game_is_final:
                # Get CFB Game data
                cfb_game_result = did_tech_die_cfb.get_result(cfb_game_data)
                home_team = cfb_game_data.home_team
                away_team = cfb_game_data.away_team
                home_pts = str(cfb_game_data.home_points)
                away_pts = str(cfb_game_data.away_points)
                recent_tweets = client.get_users_tweets(id=1353975070134329344, tweet_fields=["id"], user_auth=True)
                print(recent_tweets)
                #Create tweet
                #Todo: include sport, teams, and score in tweet
                if cfb_game_result == 'L':
                    if home_team == did_tech_die_cfb.team:
                        new_tweet = str('Yes.\n' + '🏈 ' + away_team + ' ' + away_pts + ', ' + home_team + ' ' + home_pts)
                        #Todo: check if new_tweet was already tweeted
                        if any(new_tweet not in tweets for tweets in recent_tweets.data):
                            print("Crafting tweet")
                            response = client.create_tweet(text=new_tweet)
                    else:
                        response = client.create_tweet(text='Yes.\n' + '🏈 ' + home_team + ' ' + home_pts + ', ' + away_team + ' ' + away_pts)
                if cfb_game_result == 'W':
                    if home_team == did_tech_die_cfb.team:
                        tweet = 'No.\n' + '🏈 ' + home_team + ' ' + home_pts + ', ' + away_team + ' ' + away_pts
                        if recent_tweets.meta['result_count'] == 0:
                            response = client.create_tweet(text=tweet)
                    else:
                        response = client.create_tweet(text='No.\n' + '🏈 ' + away_team + ' ' + away_pts + ', ' + home_team + ' ' + home_pts)
                

create_cfb_tweet()
#Todo: check if cfb game is final on game days after some time interval 
#Todo: when game is final: tweet and stop checking if game is final until the next game week
#print(cfb_game_data)
#print(cfb_is_today_gameday)