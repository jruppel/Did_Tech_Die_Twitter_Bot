# Tweets
import re
import constants as c
import text_alerts
import web_scraping
import game_info
import manage_db

logging,client,delay,tweet_team,seasonal_sports,boxscore_sports=c.logging,c.client,c.delay,c.tweet_team,c.seasonal_sports,c.boxscore_sports

def manage_tweets(sport):
    logging.info("Checking for recent {} games...".format(sport))
    games=web_scraping.get_website_data(seasonal_sports[sport]["url"],sport)
    if games is None:
        return
    for game in range(len(games)):
        delay
        opponent=game_info.remove_dh_from_opponent(games[game][3]) 
        game_is_exhibiton=game_info.is_game_exhibition(opponent)
        if game_is_exhibiton:
            continue
        result=games[game][5]
        game_is_final=game_info.is_game_final(result)
        if not game_is_final:
            continue
        date,time,at,links=games[game][1],game_info.nan_time_to_time(games[game][2]),games[game][4],games[game][6]
        game_has_boxscore=game_info.does_game_have_boxscore(sport,links)
        if not game_has_boxscore:
            continue
        team_record,opponent_record=get_records(sport,links)
        team_record,opponent_record=game_info.remove_blank_records_from_boxscore(team_record,opponent_record)
        is_duplicate=manage_db.is_game_in_db(sport,date,time,opponent,at,team_record,opponent_record,result)
        if is_duplicate:
            continue
        win_loss,team_score,opponent_score,separator,reg_notes,add_notes=get_score_values(sport,result)
        new_tweet=set_tweet(seasonal_sports[sport]["emoji"],opponent,win_loss,team_score,opponent_score,separator,reg_notes,add_notes,team_record,opponent_record)
        response=client.create_tweet(text=new_tweet)
        new_tweet_id=response.data['id']
        tweet_url=f"https://twitter.com/user/status/{new_tweet_id}"
        message="Link:\n{}\nTweet:\n{}".format(tweet_url,new_tweet)
        logging.info(message)
        text_alerts.send_text(message)
        logging.info("Inserting new game data in game db...")
        manage_db.insert_new_game_data(
            sport,date,time,opponent,at,result,team_record,opponent_record,new_tweet_id
            )
        incorrect_tweet_id=get_incorrect_tweet_id(
            sport,date,time,opponent,at,result,team_record,opponent_record
            )
        if incorrect_tweet_id is not None:
            delete_incorrect_tweet(incorrect_tweet_id)
            manage_db.delete_incorrect_game_data(
            incorrect_tweet_id
            )
        #game_num-=1

def get_records(sport,links):
    if sport in boxscore_sports:
        team_record,opponent_record=web_scraping.scrape_boxscore_records(links)
    else:
        team_record=opponent_record=None
    return team_record,opponent_record

def get_score_values(sport,result):
    win_loss,team_score,opponent_score,reg_notes,add_notes=game_info.result_to_score(sport,result)
    separator=get_separator(win_loss)
    return win_loss,team_score,opponent_score,separator,reg_notes,add_notes

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

def set_tweet(team_sport,opponent,win_loss,team_score,opponent_score,separator,reg_notes,add_notes,team_record,opponent_record):
    if [x for x in (win_loss,team_record,opponent_record) if x is not None]:
        if win_loss=='W' or win_loss=='T':
            pos_neg,win_team_record,win_team,lose_team_record,lose_team,win_score,lose_score="No.",team_record,tweet_team,opponent_record,opponent,team_score,opponent_score
        if win_loss=='L':
            pos_neg,win_team_record,win_team,lose_team_record,lose_team,win_score,lose_score="Yes.",opponent_record,opponent,team_record,tweet_team,opponent_score,team_score
        tweet_text="{}\n{} {} {} {} {} {} {} to {} {}.\n{}".format(pos_neg,team_sport,win_team_record,win_team,separator,lose_team_record,lose_team,win_score,lose_score,reg_notes,add_notes)
    elif [x for x in (win_loss,team_record,opponent_record) if x is None]:
        if team_score=='1st':
            pos_neg="No."
        else:
            pos_neg="Yes."
        tweet_text="{}\n{} {} {} {} at the {} {}.\n{}".format(pos_neg,team_sport,tweet_team,separator,team_score,opponent,reg_notes,add_notes)
    tweet=tweet_text.replace("  "," ").replace(" .", ".")
    return tweet

def get_incorrect_tweet_id(sport,date,time,opponent,at,result,team_record,opponent_record):
    if sport in boxscore_sports:
        gd_no_team_record=manage_db.get_game_data(sport,date,time,opponent,at,result,None,opponent_record,None)
        gd_no_opponent_record=manage_db.get_game_data(sport,date,time,opponent,at,result,team_record,None,None)
        if len(gd_no_team_record)>1:
            return gd_no_team_record[0][8]
        elif len(gd_no_opponent_record)>1:
            return gd_no_opponent_record[0][8]
    gd_no_opponent=manage_db.get_game_data(sport,date,time,None,at,result,team_record,opponent_record,None)
    gd_no_result=manage_db.get_game_data(sport,date,time,opponent,at,None,team_record,opponent_record,None)
    if len(gd_no_opponent)>1:
        return gd_no_opponent_record[0][8]
    elif len(gd_no_result)>1: 
        return gd_no_result[0][8]
    else:
        return None

def main():
    logging.info("Starting Did Tech Die Twitter bot")
    for sport in seasonal_sports:
        manage_tweets(sport)
    manage_db.delete_old_game_data()
    logging.info("Current game data:{}".format(manage_db.get_all_game_data()))
    logging.info("Ending Did Tech Die Twitter bot\n")

main()