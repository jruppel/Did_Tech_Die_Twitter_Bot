# Tweets

import constants
import text_alerts
import web_scraping
import game_info
import manage_db

logging,client,delay,team,season=constants.logging,constants.client,constants.delay,constants.team,constants.season

def create_tweets(sport):
    delay
    logging.info("Checking for recent {} games...".format(sport))
    url=web_scraping.get_sport_url(sport)
    games=web_scraping.get_website_data(url,sport)
    if games is not None:
        for game in range(len(games)):
            sport,date,time,opponent,home_away,result,incorrect_tweet_id=games[game][0],games[game][1],games[game][2],games[game][3],games[game][4],games[game][5],None
            time,game_is_exhibiton,game_is_final,is_duplicate=game_info.nan_time_to_time(time),game_info.is_game_exhibition(opponent),game_info.is_game_final(result),manage_db.is_game_in_db(sport,date,time,opponent,home_away,result)
            if not game_is_exhibiton and game_is_final and not is_duplicate:
                new_tweet=set_tweet(url,sport,opponent,result)
                response=client.create_tweet(text=new_tweet)
                new_tweet_id=response.data['id']
                url=f"https://twitter.com/user/status/{new_tweet_id}"
                message="Link:\n{}\nTweet:\n{}".format(url,new_tweet)
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

def delete_incorrect_tweet(tweet_id):
    client.delete_tweet(tweet_id)

def set_tweet(url,sport,opponent,result):
    team_sport=game_info.get_team_sport(sport)
    win_loss,tech_score,opponent_score,reg_notes,add_notes=game_info.result_to_score(sport,result)
    team_record,opponent_record=web_scraping.get_boxscore_records(url,opponent)
    if win_loss==opponent_score==None:
        if tech_score=='1st':
            tweet="No.\n{}: {} finished {} at the {}.".format(team_sport,team,tech_score,opponent)
        else:
            tweet="Yes.\n{}: {} finished {} at the {}.".format(team_sport,team,tech_score,opponent)
    elif add_notes:
        if win_loss=='W':
            tweet="No.\n{}: {} defeats {} {} to {} {}.\n{}.".format(
                team_sport,team_record,team,opponent_record,opponent,tech_score,opponent_score,reg_notes,add_notes
                ) 
        elif win_loss=='T':
            tweet="No.\n{}: {} {} ties {} {} {} to {} {}.\n{}.".format(
                team_sport,team_record,team,opponent_record,opponent,tech_score,opponent_score,reg_notes,add_notes
                )
        elif win_loss=='L':
            tweet="Yes.\n{}: {} {} defeats {} {} {} to {} {}.\n{}.".format(
                team_sport,opponent_record,opponent,team_record,team,opponent_score,tech_score,reg_notes,add_notes
                ) 
    elif reg_notes:
        if win_loss=='W':
            tweet="No.\n{}: {} {} defeats {} {} {} to {} {}.".format(
                team_sport,team_record,team,opponent_record,opponent,tech_score,opponent_score,reg_notes
                ) 
        elif win_loss=='T':
            tweet="No.\n{}: {} {} ties {} {} {} to {} {}.".format(
                team_sport,team_record,team,opponent_record,opponent,tech_score,opponent_score,reg_notes
                )
        elif win_loss=='L':
            tweet="Yes.\n{}: {} {} defeats {} {} {} to {} {}.".format(
                team_sport,opponent_record,opponent,team_record,team,opponent_score,tech_score,reg_notes
                )
    else:
        if win_loss=='W':
            tweet="No.\n{}: {} {} defeats {} {} {} to {}.".format(
                team_sport,team_record,team,opponent_record,opponent,tech_score,opponent_score
                ) 
        elif win_loss=='T':
            tweet = "No.\n{}: {} {} ties {} {} {} to {}.".format(
                team_sport,team_record,team,opponent_record,opponent,tech_score,opponent_score
                )
        elif win_loss == 'L':
            tweet = "Yes.\n{}: {} {} defeats {} {} {} to {}.".format(
                team_sport,opponent_record,opponent,team_record,team,opponent_score,tech_score
                )
    return tweet

def get_incorrect_tweet(sport, date, time, opponent, home_away, result):
    game_data = manage_db.get_game_data(sport, date, time, opponent, home_away, result)
    row_count = len(game_data)-1
    tweet_id = None
    if result == None:
        logging.info("Number of tweets with incorrect result: {}".format(row_count))
    if opponent == None:
        logging.info("Number of tweets with incorrect opponent: {}".format(row_count))
    if row_count >= 1:
        tweet_id = game_data[0][6]
    return tweet_id

def tweet_seasonal_sports():
    if season == 'winter':
        for sport in constants.winter_sports:
            create_tweets(sport)
    elif season == 'spring':
        for sport in constants.spring_sports:
            create_tweets(sport)
    elif season == 'summer':
        for sport in constants.summer_sports:
            create_tweets(sport)
    elif season == 'autumn':
        for sport in constants.autumn_sports:
            create_tweets(sport)
def main():
    logging.info("Starting Did Tech Die Twitter bot")
    tweet_seasonal_sports()
    logging.info("Ending Did Tech Die Twitter bot\n")

main()