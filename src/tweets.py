# Tweets
import re
from datetime import datetime
import constants
import tweet_alerts
import web_scraping
import game_info
import manage_db

logging=constants.logging
client=constants.client
delay=constants.delay
tweet_team=constants.tweet_team
seasonal_sports=constants.seasonal_sports
boxscore_sports=constants.boxscore_sports
tech_ids=constants.tech_ids
tech_names=constants.tech_names

def manage_tweets(sport):
    sport_id=seasonal_sports[sport]["sport_id"]
    sport_year=seasonal_sports[sport]["year"]
    logging.info("Checking for recent {} games...".format(sport))
    recent_games=web_scraping.get_sport_schedule_recent_games(sport_id,sport_year)
    if recent_games is None:
        return
    for game in recent_games:
        delay
        result=game["result"]
        if result is None:
            continue
        schedule_opponent=game_info.remove_extra_chars_from_opponent(game["opponent"]["title"])
        if game_info.is_game_exhibition(schedule_opponent):
            continue
        game_id=game["id"]
        game_date=datetime.fromisoformat(game["date"]).date()
        time=game_info.nan_time_to_time(game["time"])
        at=game["atVs"]
        tournament=(
            game["tournament"]["title"]
            if game["tournament"] is not None
            else None
        )
        notes=result["postscoreInfo"]
        results_data=web_scraping.get_results_data(sport_id,game_id)
        if results_data is None:
            continue
        win_loss=results_data["resultStatus"]
        separator=get_separator(win_loss)
        boxscore=results_data["boxscore"]
        if boxscore is not None:
            home=boxscore["home"]
            away=boxscore["away"]
            if home["id"] in constants.tech_ids or home["name"] in constants.tech_names:
                tech_team=home
                opponent_team=away
            else:
                tech_team=away
                opponent_team=home
            opponent_name=opponent_team["name"]    
            tech_score=int(tech_team["score"])
            opponent_score=int(opponent_team["score"])
            tech_record=game_info.get_overall_record(tech_team["record"])
            opponent_record=game_info.get_overall_record(opponent_team["record"])
        else:
            opponent_name=game["opponent"]["title"]
            tech_score=result["postscoreInfo"]
            opponent_score=""
            tech_record=""
            opponent_record=""
            if tech_score=="":
                continue
            if sport in {'womens-bowling','mens-golf'}:
                continue
            #For these sports, there is one page for both T&F and cross country
            # #So I split the results and return only the result the specific sport. Later, the other sport will be returned as well
            if sport in {'mens-track-and-field','womens-track-and-field','mens-cross-country','womens-cross-country'}:
                parts=[part.strip() for part in tech_score.split(";")]
                index = 0 if sport in {"mens-track-and-field", "mens-cross-country"} else 1
                tech_score = parts[index].split()[1]      
        #is_duplicate=manage_db.is_game_in_db(game_id,sport,game_date,time,opponent,at,team_record,opponent_record,result)
        #if is_duplicate:
        #    continue
        #win_loss,team_score,opponent_score,separator,reg_notes,add_notes=get_score_values(sport,result)
        new_tweet=set_tweet(seasonal_sports[sport]["emoji"],opponent_name,win_loss,tech_score,opponent_score,separator,notes,tech_record,opponent_record,tournament)
        print(new_tweet)
        #response=client.create_tweet(text=new_tweet)
        #new_tweet_id=response.data['id']
        #tweet_url=f"https://twitter.com/user/status/{new_tweet_id}"
        #message="Link:\n{}\nTweet:\n{}".format(tweet_url,new_tweet)
        #logging.info(message)
        #tweet_alerts.send_tweet_notification(tweet_url,new_tweet)
        #logging.info("Inserting new game data in game db...")
        #manage_db.insert_new_game_data(
        #    game_num,sport,date,time,opponent,at,result,team_record,opponent_record,new_tweet_id
        #    )
        #incorrect_tweet_id=get_incorrect_tweet_id(
        #    game_num,sport,date,time
        #    )
        #if incorrect_tweet_id is not None:
        #    client.delete_tweet(incorrect_tweet_id)
        #    manage_db.delete_incorrect_game_data(
        #    incorrect_tweet_id
        #    )
def get_records(sport,links):
    if sport in boxscore_sports:
        team_record,opponent_record=web_scraping.scrape_boxscore_records(links)
    else:
        team_record=opponent_record=""
    return team_record,opponent_record

def get_score_values(sport,result):
    win_loss,team_score,opponent_score,reg_notes,add_notes=game_info.result_to_score(sport,result)
    separator=get_separator(win_loss)
    return win_loss,team_score,opponent_score,separator,reg_notes,add_notes

def get_separator(win_loss):
    if win_loss=='W' or win_loss=='L':
        separator="defeats"
    elif win_loss=='T':
        separator="ties"
    elif win_loss=='N':
        separator="finished"
    return separator

def set_tweet(team_sport,opponent,win_loss,tech_score,opponent_score,separator,notes,tech_record,opponent_record,tournament):
    if win_loss=='W' or win_loss=='T':
        did_tech_die="No."
        win_team_record=tech_record
        win_team=tweet_team
        lose_team_record=opponent_record
        lose_team=opponent
        win_score=tech_score
        lose_score=opponent_score
        tweet_text="{}\n{}: {} {} {} {} {} {} to {} {}.".format(did_tech_die,team_sport,win_team_record,win_team,separator,lose_team_record,lose_team,win_score,lose_score,notes)
    elif win_loss=='L':
        did_tech_die="Yes."
        win_team_record=opponent_record
        win_team=opponent
        lose_team_record=tech_record
        lose_team=tweet_team
        win_score=opponent_score
        lose_score=tech_score
        tweet_text="{}\n{}: {} {} {} {} {} {} to {} {}.".format(did_tech_die,team_sport,win_team_record,win_team,separator,lose_team_record,lose_team,win_score,lose_score,notes)
    else:
        did_tech_die="N/A."
        tweet_text="{}\n{}: {} {} {} at the {}.".format(did_tech_die,team_sport,tweet_team,separator,tech_score,opponent)
    tweet=tweet_text.replace("  "," ").replace(" .", ".")
    return tweet

def get_incorrect_tweet_id(game_num,sport,date,time):
    incorrect_game_data=manage_db.get_game_data(game_num,sport,date,time,None,None,None,None,None,None)
    if len(incorrect_game_data)>1:
        return incorrect_game_data[0][9]
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