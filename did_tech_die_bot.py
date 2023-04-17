from datetime import date, datetime
import logging
import random
import time as tm
import tweepy
import constants
import did_tech_die
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

testing = constants.testing

logging.basicConfig(
     filename=constants.log,
     level=logging.DEBUG, 
     format= '[%(asctime)s] {%(module)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%m-%d-%Y %H:%M:%S'
 )

# Set testing account constants
if testing:
    consumer_key = constants.test_twitter_consumer_key
    consumer_secret = constants.test_twitter_consumer_secret
    access_token = constants.test_twitter_access_token
    access_token_secret = constants.test_twitter_access_token_secret
    bearer_token = constants.test_twitter_bearer_token

# Set main account constants
else:
    consumer_key = constants.twitter_consumer_key
    consumer_secret = constants.twitter_consumer_secret
    access_token = constants.twitter_access_token
    access_token_secret = constants.twitter_access_token_secret
    bearer_token = constants.twitter_bearer_token

#Authenticate to Twitter
client = tweepy.Client(bearer_token=bearer_token,consumer_key=consumer_key,consumer_secret=consumer_secret,access_token=access_token,access_token_secret=access_token_secret)

#Set texting 
smtp_provider=constants.smtp_provider
recipient=constants.recipient
email=constants.email
password=constants.password

#Todo: Refactor mass tweeting
Y = 2000 # dummy leap year to allow input X-02-29 (leap day)
seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
           ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
           ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
           ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
           ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]
winter_sports = {'football', 'mens-basketball', 'womens-basketball', 'baseball', 'softball', 'womens-tennis', 'womens-bowling', 'mens-golf', 'womens-track-and-field', 'mens-track-and-field'}
spring_sports = {'mens-basketball', 'womens-basketball', 'baseball', 'softball', 'womens-tennis', 'womens-bowling', 'mens-golf', 'womens-track-and-field', 'mens-track-and-field'}
summer_sports = {'football', 'womens-volleyball', 'womens-cross-country', 'womens-soccer', 'mens-cross-country', 'mens-golf'}
autumn_sports = {'football', 'mens-basketball', 'womens-basketball', 'womens-volleyball', 'womens-tennis', 'womens-bowling', 'womens-soccer', 'mens-golf'}

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
    logging.info("Checking for recent {} games...".format(sport))
    url = did_tech_die.get_tech_url(sport)
    games = did_tech_die.get_website_data(url, sport)
    if games is not None:
        for game in range(len(games)):
            sport, date, time, opponent, home_away, result = games[game][0], games[game][1], games[game][2], games[game][3], games[game][4], games[game][5]
            #Todo: assign each value of game for did_tech_die functions to reduce redundant code
            logging.info("Checking if {} game {} is an exhibition...".format(sport, game+1))
            game_is_exhibibiton = did_tech_die.is_game_exhibition(opponent)
            if not game_is_exhibibiton:
                logging.info("Checking if {} game {} is final...".format(sport, game+1))
                game_is_final = did_tech_die.is_game_final(result)
                if game_is_final:
                        time = did_tech_die.nan_time_to_time(time)
                        logging.info("Checking if tweet is duplicated...")
                        is_duplicate = did_tech_die.is_game_in_db(sport, date, time, opponent, home_away, result)
                        if not is_duplicate:
                            new_tweet = did_tech_die.set_tweet(sport, opponent, result)
                            response = client.create_tweet(text=new_tweet)
                            tweet_id = response.data['id']
                            url = f"https://twitter.com/user/status/{tweet_id}"
                            message = "Link:\n{}\nTweet:\n{}".format(url, new_tweet)
                            logging.info(message)
                            send_text(message)
                            logging.info("Updating game data in game db...")
                            did_tech_die.update_game_data(sport, date, time, opponent, home_away, result, id=tweet_id)
                            delete_incorrect_tweet(sport, date, time, opponent, home_away, result)
                            # Todo: If there are two rows of the same game with different results/opponent names, 
                            # delete the first row and delete the first tweet since it's old and incorrect data


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

def send_text(message):
    server = smtplib.SMTP(smtp_provider, 587)
    server.starttls()
    server.login(email, password)
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = recipient
    # Make sure you add a new line in the subject
    msg['Subject'] = "New tweet\n"
    msg.attach(MIMEText(message, 'plain'))
    sms = msg.as_string()
    server.sendmail(email,recipient,sms)

def delete_incorrect_tweet(gd_sport, gd_date, gd_time, gd_opponent, gd_home_away, gd_result):
    tweet_id_with_incorrect_result = did_tech_die.get_incorrect_tweet(sport=gd_sport, date=gd_date, time=gd_time, opponent=gd_opponent, home_away=gd_home_away, result=None)
    tweet_id_with_incorrect_opponent = did_tech_die.get_incorrect_tweet(sport=gd_sport, date=gd_date, time=gd_time, opponent=None, home_away=gd_home_away, result=gd_result)
    logging.info("Tweet ID with incorrect result: {}".format(tweet_id_with_incorrect_result))
    logging.info("Tweet ID with incorrect opponent: {}".format(tweet_id_with_incorrect_opponent))
    if tweet_id_with_incorrect_result is not None:
        client.delete_tweet(tweet_id_with_incorrect_result)
    if tweet_id_with_incorrect_opponent is not None:
        client.delete_tweet(tweet_id_with_incorrect_opponent)

def main():
    logging.info("Starting Did Tech Die Twitter bot")
    tweet_seasonal_sports()
    logging.info("Ending Did Tech Die Twitter bot\n")

main()