# Tweets
import re
import constants
import text_alerts
import web_scraping
import game_info
import manage_db

logging,client,delay,team,season,winter_sports,spring_sports,summer_sports,autumn_sports,boxscore_sports=constants.logging,constants.client,constants.delay,constants.team,constants.season,constants.winter_sports,constants.spring_sports,constants.summer_sports,constants.autumn_sports,constants.boxscore_sports

def manage_tweets(sport):
    logging.info("Checking for recent {} games...".format(sport))
    url=web_scraping.get_sport_url(sport)
    games=web_scraping.get_website_data(url,sport)
    if games is None:
        return
    game_num=len(games)
    for game in range(game_num):
        delay
        sport,date,time,opponent,home_away,result,team_record,opponent_record,incorrect_tweet_id=games[game][0],games[game][1],games[game][2],games[game][3],games[game][4],games[game][5],None,None,None
        time,game_is_exhibiton,game_is_final,is_duplicate=game_info.nan_time_to_time(time),game_info.is_game_exhibition(opponent),game_info.is_game_final(result),manage_db.is_game_in_db(sport,date,time,opponent,home_away,result)
        if game_is_exhibiton or not game_is_final or is_duplicate:
            return
        if sport in boxscore_sports:
            team_record,opponent_record=web_scraping.get_boxscore_records(url,game_num)
        new_tweet=set_tweet(sport,opponent,result,team_record,opponent_record)
        response=client.create_tweet(text=new_tweet)
        new_tweet_id=response.data['id']
        tweet_url=f"https://twitter.com/user/status/{new_tweet_id}"
        message="Link:\n{}\nTweet:\n{}".format(tweet_url,new_tweet)
        logging.info(message)
        text_alerts.send_text(message)
        logging.info("Inserting new game data in game db...")
        manage_db.insert_new_game_data(
            sport,date,time,opponent,home_away,result,new_tweet_id
            )
        manage_db.delete_old_game_data()
        incorrect_tweet_id=get_incorrect_tweet(
            sport,date,time,opponent,home_away,result
            )
        if incorrect_tweet_id is not None:
            delete_incorrect_tweet(incorrect_tweet_id)
            manage_db.delete_incorrect_game_data(
            sport,date,time,opponent,home_away,result,incorrect_tweet_id
            )
        game_num-=1
            

def delete_incorrect_tweet(tweet_id):
    client.delete_tweet(tweet_id)

def get_separator(win_loss):
    if win_loss=='W' or win_loss=='L':
        separator="defeats"
    elif win_loss=='T':
        separator="ties"
    elif win_loss==None:
        separator="finished"
    return separator

def set_tweet(sport,opponent,result,team_record,opponent_record):
    team_sport=game_info.get_team_sport(sport)
    win_loss,team_score,opponent_score,reg_notes,add_notes=game_info.result_to_score(sport,result)
    separator=get_separator(win_loss)
    if [x for x in (win_loss,team_record,opponent_record) if x is not None]:
        if win_loss=='W' or win_loss=='T':
            pos_neg,win_team_record,win_team,lose_team_record,lose_team,win_score,lose_score="No.",team_record,team,opponent_record,opponent,team_score,opponent_score
        if win_loss=='L':
            pos_neg,win_team_record,win_team,lose_team_record,lose_team,win_score,lose_score="Yes.",opponent_record,opponent,team_record,team,opponent_score,team_score
        tweet_text="{}\n{} {} {} {} {} {} {} to {} {}.\n{}".format(pos_neg,team_sport,win_team_record,win_team,separator,lose_team_record,lose_team,win_score,lose_score,reg_notes,add_notes)
    elif [x for x in (win_loss,team_record,opponent_record) if x is None]:
        if team_score=='1st':
            pos_neg="No."
        else:
            pos_neg="Yes."
        tweet_text="{}\n{} {} {} {} at the {} {}.\n{}".format(pos_neg,team_sport,team,separator,team_score,opponent,reg_notes,add_notes)
    tweet=tweet_text.replace("  "," ").replace(" .", ".")
    return tweet

def get_incorrect_tweet(sport,date,time,opponent,home_away,result):
    game_data=manage_db.get_game_data(sport,date,time,opponent,home_away,result)
    row_count=len(game_data)-1
    tweet_id=None
    if result==None:
        logging.info("Number of tweets with incorrect result: {}".format(row_count))
    if opponent==None:
        logging.info("Number of tweets with incorrect opponent: {}".format(row_count))
    if row_count>=1:
        tweet_id=game_data[0][6]
    return tweet_id

def tweet_seasonal_sports():
    if season=='winter':
        for sport in winter_sports:
            manage_tweets(sport)
    elif season=='spring':
        for sport in spring_sports:
            manage_tweets(sport)
    elif season=='summer':
        for sport in summer_sports:
            manage_tweets(sport)
    elif season=='autumn':
        for sport in autumn_sports:
            manage_tweets(sport)
def main():
    logging.info("Starting Did Tech Die Twitter bot")
    tweet_seasonal_sports()
    logging.info("Ending Did Tech Die Twitter bot\n")

main()