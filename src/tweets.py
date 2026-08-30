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
        return 0, 0

    created_count = 0
    updated_count = 0

    for game in recent_games:
        opponent_name = game.get("opponent", {}).get("title", "")
        if game_info.is_game_exhibition(opponent_name):
            continue

        game_id = str(game.get("id", ""))
        results_data = web_scraping.get_results_data(sport_id, game_id)
        if not results_data:
            logging.info(f"Game {game_id} vs {opponent_name} ({sport}) has no results posted yet; skipping.")
            continue

        game_data = game_info.extract_game_details(game, sport, results_data)
        if not game_data:
            logging.info(f"Game {game_id} vs {opponent_name} ({sport}) has no final score yet; skipping.")
            continue

        win_loss = game_data["result_status"]
        separator = get_separator(win_loss)
        post_text = set_post(
            seasonal_sports[sport]["emoji"],
            game_data["opponent"],
            win_loss,
            game_data["team_score"],
            game_data["opponent_score"],
            separator,
            game_data["notes"],
            game_data["team_record"],
            game_data["opponent_record"]
        )

        existing_game = db.get_game_data(game_id)
        if existing_game is not None:
            if db.has_game_changed(existing_game, game_data):
                logging.info(f"Game change detected for {game_id} vs {opponent_name}")
                if existing_game.post_id:
                    if replace_post(game_id, post_text, old_post_id=existing_game.post_id):
                        logging.info(f"Replacing tweet {existing_game.post_id}")
                        db.increment_correction_count(game_id)
                        updated_count += 1
                db.update_game(
                    game_id,
                    home_away=game_data["home_away"],
                    opponent=game_data["opponent"],
                    team_score=game_data["team_score"],
                    opponent_score=game_data["opponent_score"],
                    team_record=game_data["team_record"],
                    opponent_record=game_data["opponent_record"],
                    result_status=game_data["result_status"],
                    notes=game_data["notes"]
                )
            else:
                logging.info(f"Game {game_id} vs {opponent_name} ({sport}) already up-to-date; skipping.")
            continue

        if testing:
            logging.info(f"TEST MODE - Would create post:\n{post_text}")
            post_id = f"TEST_{game_id}"
            created_count += 1
        else:
            try:
                response = client.create_tweet(text=post_text)
                post_id = response.data["id"]
                tweet_url = f"https://twitter.com/user/status/{post_id}"
                logging.info(f"Link:\n{tweet_url}\nTweet:\n{post_text}")
                tweet_alerts.send_tweet_notification(tweet_url, post_text)
                created_count += 1
            except Exception as e:
                logging.error(f"Failed creating post for game {game_id}: {e}")
                post_id = None

        game_data["post_id"] = post_id
        game_data["post_text"] = post_text
        db.insert_game(game_data)

    return created_count, updated_count

def main():
    logging.info("Starting Did Tech Die Twitter bot")
    total_created = 0
    total_updated = 0
    for sport in seasonal_sports:
        created, updated = process_games(sport)
        total_created += created
        total_updated += updated
    logging.info(f"Run completed: {total_created} new tweets created, {total_updated} tweets updated.\n")

if __name__ == "__main__":
    main()