# Tweets
from datetime import datetime
import constants
import database
import game_info
import tweet_alerts
import web_scraping

logging = constants.logging
client = constants.client
tweet_team = constants.tweet_team
seasonal_sports = constants.seasonal_sports
boxscore_sports = constants.boxscore_sports
tech_ids = constants.tech_ids
tech_names = constants.tech_names
testing = constants.testing

db = database.Database(constants.sql_db)

def get_separator(win_loss):
    if win_loss in {'W', 'L'}:
        return "defeats"
    elif win_loss == 'T':
        return "ties"
    elif win_loss == 'N':
        return "finished"
    return "vs"

def set_post(team_sport, opponent, win_loss, tech_score, opponent_score, separator, notes, tech_record, opponent_record):
    if win_loss in {'W', 'T'}:
        did_tech_die = "No."
        win_team_record = tech_record
        win_team = tweet_team
        lose_team_record = opponent_record
        lose_team = opponent
        win_score = tech_score
        lose_score = opponent_score
        post_text = f"{did_tech_die}\n{team_sport}: {win_team_record} {win_team} {separator} {lose_team_record} {lose_team} {win_score} to {lose_score} {notes}."
    elif win_loss == 'L':
        did_tech_die = "Yes."
        win_team_record = opponent_record
        win_team = opponent
        lose_team_record = tech_record
        lose_team = tweet_team
        win_score = opponent_score
        lose_score = tech_score
        post_text = f"{did_tech_die}\n{team_sport}: {win_team_record} {win_team} {separator} {lose_team_record} {lose_team} {win_score} to {lose_score} {notes}."
    else:
        did_tech_die = "N/A."
        post_text = f"{did_tech_die}\n{team_sport}: {tweet_team} {separator} {tech_score} at the {opponent}."
    
    post = post_text.replace("  ", " ").replace(" .", ".")
    return post

def get_post_id(game_id):
    game = db.get_game_data(game_id)
    return game.post_id if game else None

def replace_post(game_id, new_post, old_post_id=None):
    if testing:
        logging.info(f"TEST MODE - Would replace post for game {game_id}:\n{new_post}")
        return True

    if old_post_id is None:
        old_post_id = get_post_id(game_id)
    logging.info(f"Old post id: {old_post_id}")

    try:
        response = client.create_tweet(text=new_post)
        new_post_id = response.data["id"]
    except Exception as e:
        logging.error(f"Failed creating replacement post for game {game_id}: {e}")
        return False

    if old_post_id:
        try:
            client.delete_tweet(old_post_id)
            logging.info(f"Deleted old post {old_post_id}")
        except Exception as e:
            logging.warning(f"Could not delete old post {old_post_id}: {e}")

    db.mark_posted(game_id, new_post_id, new_post)
    logging.info(f"Replaced post with {new_post_id}")
    return True

def process_games(sport):
    sport_id = seasonal_sports[sport]["sport_id"]
    sport_year = seasonal_sports[sport]["year"]
    logging.info(f"Checking for recent {sport} games...")
    recent_games = web_scraping.get_sport_schedule_recent_games(sport_id, sport_year)
    if not recent_games:
        return

    for game in recent_games:
        result = game.get("result")
        if result is None:
            continue

        opponent_name = game.get("opponent", {}).get("title", "")
        if game_info.is_game_exhibition(opponent_name):
            continue

        game_id = str(game["id"])
        game_date = datetime.fromisoformat(game["date"]).date()
        time = game_info.nan_time_to_time(game.get("time"))
        home_away = game.get("atVs", "")
        notes = result.get("postscoreInfo", "")

        results_data = web_scraping.get_results_data(sport_id, game_id)
        if results_data is None:
            continue

        win_loss = results_data.get("resultStatus", "")
        separator = get_separator(win_loss)
        boxscore = results_data.get("boxscore")

        if boxscore is not None:
            home = boxscore.get("home", {})
            away = boxscore.get("away", {})
            if home.get("id") in tech_ids or home.get("name") in tech_names:
                tech_team = home
                opponent_team = away
            else:
                tech_team = away
                opponent_team = home
            tech_score = tech_team.get("score", "")
            opponent_score = opponent_team.get("score", "")
            tech_record = game_info.get_overall_record(tech_team.get("record", ""))
            opponent_record = game_info.get_overall_record(opponent_team.get("record", ""))
        else:
            tech_record = ""
            opponent_record = ""
            tech_score = (
                result.get("teamScore")
                or result.get("postscoreInfo")
                or result.get("prescoreInfo")
                or ""
            )
            if not tech_score:
                continue
            opponent_score = result.get("opponentScore", "")

            # Track & Field / Cross Country result parsing
            if sport in constants.TRACK_AND_FIELD_SPORTS:
                parts = [part.strip() for part in tech_score.split(";")]
                index = 0 if sport in {"mens-track-and-field", "mens-cross-country"} else 1
                if len(parts) > index and len(parts[index].split()) > 1:
                    tech_score = parts[index].split()[1]

        # Single DB lookup in memory
        existing_game = db.get_game_data(game_id)

        if existing_game is not None:
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
            if db.has_game_changed(existing_game, current_game):
                logging.info(f"Game change detected for {game_id}")
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
                if existing_game.post_id:
                    if replace_post(game_id, corrected_post, old_post_id=existing_game.post_id):
                        logging.info(f"Replacing tweet {existing_game.post_id}")
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
            continue

        new_post = set_post(
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

        if testing:
            logging.info(f"TEST MODE - Would create post:\n{new_post}")
            post_id = f"TEST_{game_id}"
        else:
            try:
                response = client.create_tweet(text=new_post)
                post_id = response.data["id"]
                tweet_url = f"https://twitter.com/user/status/{post_id}"
                logging.info(f"Link:\n{tweet_url}\nTweet:\n{new_post}")
                tweet_alerts.send_tweet_notification(tweet_url, new_post)
            except Exception as e:
                logging.error(f"Failed creating post for game {game_id}: {e}")
                post_id = None

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

def main():
    logging.info("Starting Did Tech Die Twitter bot")
    for sport in seasonal_sports:
        process_games(sport)
    logging.info("Ending Did Tech Die Twitter bot\n")

if __name__ == "__main__":
    main()