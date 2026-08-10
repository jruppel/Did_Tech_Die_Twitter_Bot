# Tweets
from datetime import datetime
import constants
import tweet_alerts
import web_scraping
import game_info
import database

logging=constants.logging
client=constants.client
tweet_team=constants.tweet_team
seasonal_sports=constants.seasonal_sports
boxscore_sports=constants.boxscore_sports
tech_ids=constants.tech_ids
tech_names=constants.tech_names
testing=constants.testing

db = database.Database(constants.sql_db)

def process_games(sport):
    sport_id=seasonal_sports[sport]["sport_id"]
    sport_year=seasonal_sports[sport]["year"]
    logging.info("Checking for recent {} games...".format(sport))
    recent_games=web_scraping.get_sport_schedule_recent_games(sport_id,sport_year)
    if recent_games is None:
        return
    for game in recent_games:
        result=game["result"]
        if result is None:
            continue
        #schedule_opponent=game_info.remove_extra_chars_from_opponent(game["opponent"]["title"])
        if game_info.is_game_exhibition(game["gamePromotionText"]):
            continue
        game_id=game["id"]
        game_date=datetime.fromisoformat(game["date"]).date()
        time=game_info.nan_time_to_time(game["time"])
        home_away=game["atVs"]
        #tournament=(
        #    game["tournament"]["title"]
        #    if game["tournament"]
        #    else None
        #)
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
            if home["id"] in tech_ids or home["name"] in tech_names:
                tech_team=home
                opponent_team=away
            else:
                tech_team=away
                opponent_team=home
            opponent_name=opponent_team["name"]    
            tech_score=tech_team["score"]
            opponent_score=opponent_team["score"]
            tech_record=game_info.get_overall_record(tech_team["record"])
            opponent_record=game_info.get_overall_record(opponent_team["record"])
        else:
            opponent_name=game["opponent"]["title"]
            tech_record=""
            opponent_record=""
            tech_score=(
                result.get("teamScore")
                or result.get("postscoreInfo")
                or result.get("prescoreInfo")
                or ""
            )
            if not tech_score: 
                continue
            opponent_score = result.get("opponentScore", "")
            #For these sports, there is one page for both T&F and cross country
            #So I split the results and return only the result the specific sport. Later, the other sport will be returned as well
            if sport in constants.TRACK_AND_FIELD_SPORTS:
                parts=[part.strip() for part in tech_score.split(";")]
                index = 0 if sport in {"mens-track-and-field", "mens-cross-country"} else 1
                tech_score=parts[index].split()[1]        
        if db.has_game(game_id):
            current_game = {
                "team_record": tech_record,
                "team_score": tech_score,
                "opponent_record": opponent_record,
                "opponent": opponent_name,
                "opponent_score": opponent_score,
                "home_away": home_away,
                "result_status": win_loss,
                "notes": notes
            }  
            if db.has_game_changed(game_id, current_game):
                logging.info("Game changed detected")
                corrected_post = set_post(
                seasonal_sports[sport]["emoji"],
                opponent_name,
                win_loss,
                tech_score,
                opponent_score,
                separator,
                notes,
                tech_record,
                opponent_record
                )
                if db.has_post(game_id):
                    if replace_post(game_id, corrected_post):
                        logging.info(f"Replacing tweet {get_post_id(game_id)}")
                        db.increment_correction_count(game_id)
                db.update_game(
                    game_id,
                    home_away=home_away,
                    opponent=opponent_name,
                    team_score=tech_score,
                    opponent_score=opponent_score,
                    team_record=tech_record,
                    opponent_record=opponent_record,
                    result_status=win_loss,
                    notes=notes
                )
                logging.info(f"After update changed? {db.has_game_changed(game_id, current_game)}")
            continue
        #win_loss,team_score,opponent_score,separator,reg_notes,add_notes=get_score_values(sport,result)
        new_post=set_post(seasonal_sports[sport]["emoji"],opponent_name,win_loss,tech_score,opponent_score,separator,notes,tech_record,opponent_record)
        if testing:
            logging.info(f"TEST MODE - Would create post:\n{new_post}")
            post_id = "TEST_" + str(game_id)
        else:
            response = client.create_tweet(text=new_post)
            post_id = response.data["id"]
            tweet_url=f"https://twitter.com/user/status/{post_id}"
            message="Link:\n{}\nTweet:\n{}".format(tweet_url,new_post)
            logging.info(message)
            tweet_alerts.send_tweet_notification(tweet_url,new_post)
        db.insert_game({
        "game_id": game_id,
        "sport": sport,
        "date": str(game_date),
        "time": time,
        "opponent": opponent_name,
        "home_away": home_away,
        "result_status": win_loss,
        "team_score": tech_score,
        "opponent_score": opponent_score,
        "team_record": tech_record,
        "opponent_record": opponent_record,
        "notes": notes,
        "post_id": post_id,
        "post_text": new_post,
        })
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

def set_post(team_sport,opponent,win_loss,tech_score,opponent_score,separator,notes,tech_record,opponent_record):
    if win_loss=='W' or win_loss=='T':
        did_tech_die="No."
        win_team_record=tech_record
        win_team=tweet_team
        lose_team_record=opponent_record
        lose_team=opponent
        win_score=tech_score
        lose_score=opponent_score
        post_text="{}\n{}: {} {} {} {} {} {} to {} {}.".format(did_tech_die,team_sport,win_team_record,win_team,separator,lose_team_record,lose_team,win_score,lose_score,notes)
    elif win_loss=='L':
        did_tech_die="Yes."
        win_team_record=opponent_record
        win_team=opponent
        lose_team_record=tech_record
        lose_team=tweet_team
        win_score=opponent_score
        lose_score=tech_score
        post_text="{}\n{}: {} {} {} {} {} {} to {} {}.".format(did_tech_die,team_sport,win_team_record,win_team,separator,lose_team_record,lose_team,win_score,lose_score,notes)
    else:
        did_tech_die="N/A."
        post_text="{}\n{}: {} {} {} at the {}.".format(did_tech_die,team_sport,tweet_team,separator,tech_score,opponent)
    post=post_text.replace("  "," ").replace(" .", ".")
    return post

def get_post_id(game_id):
    game = db.get_game_data(game_id)
    if game is None:
        return None
    return game.post_id

def replace_post(game_id, new_post):
    if testing:
        logging.info(
            f"TEST MODE - Would replace post for game {game_id}:\n{new_post}"
        )
        return True
    old_post_id = get_post_id(game_id)
    logging.info(f"Old post id: {old_post_id}")
    try:
        response = client.create_tweet(text=new_post)
        new_post_id = response.data["id"]
    except Exception as e:
        logging.error(f"Failed creating replacement post: {e}")
        return False
    if old_post_id:
        try:
            client.delete_tweet(old_post_id)
            logging.info(f"Deleted old post {old_post_id}")
        except Exception as e:
            logging.warning(f"Could not delete old post: {e}")
    db.mark_posted(
        game_id,
        new_post_id,
        new_post
    )
    logging.info(f"Replaced post with {new_post_id}")
    return True

def main():
    logging.info("Starting Did Tech Die Twitter bot")
    for sport in seasonal_sports:
        process_games(sport)
    #database.delete_old_game_data()
    logging.info("Current game data:{}".format(db.get_all_game_data()))
    logging.info("Ending Did Tech Die Twitter bot\n")

main()