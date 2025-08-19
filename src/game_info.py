# Game Info
import re
import constants

logging,boxscore_sports,no_boxscore_sports=constants.logging,constants.boxscore_sports,constants.no_boxscore_sports

def remove_dh_from_opponent(opponent):
    if '(DH)' in opponent:
        opponent,*_ = opponent.partition('(DH)') 
    return opponent

def is_game_exhibition(opponent):
    exhibition=False
    if "exhibition" in opponent.lower():
        exhibition=True
        logging.info("This Tech game is an exhibition; no tweet needed!")
    else:
        logging.info("This Tech game is not an exhibition!")
    return exhibition

def is_game_final(result):
    final=False
    if not result!=result and result not in {None,'Canceled','Cancelled','Postponed',''}:
        final=True
        logging.info("This Tech game is final!")
    else:
        logging.info("This Tech game is not final!\nResult: {}".format(result))
    return final

def does_game_have_boxscore(sport,links):
    if sport in no_boxscore_sports:
        boxscore=True
        logging.info("No boxscore needed!")
    elif sport in boxscore_sports and "boxscore" in links:
        boxscore=True
        logging.info("This Tech game has a boxscore!")
    else:
        boxscore=False
        logging.info("This Tech game should have, but does not have a boxscore!\nLinks: {}".format(links))
    return boxscore

def remove_blank_records_from_boxscore(team_record,opponent_record):
    if team_record in {' ','()'}:
        team_record=''
    if opponent_record in {' ','()'}:
        opponent_record=''
    return team_record,opponent_record

def result_to_score(sport,result):
    reg_notes=add_notes=""
    win_loss_tie=["W","L","T"]
    win_loss=None
    if result[0].isdigit():
        #Retain only the resulting place
        result=result.partition(" ")[0]
        win_loss=opponent_score=None
        if sport in {'womens-bowling','mens-golf'}:
            tech_score=result
        #For these sports, there is one page for both T&F and cross country
        #So I split the results and return only the result the specific sport. Later, the other sport will be returned as well
        if sport in {'mens-track-and-field','womens-track-and-field','mens-cross-country','womens-cross-country'}:
            results = re.split('[;:]', result)
            tech_score=results[0].split(" ")[1] if sport in {'mens-track-and-field','mens-cross-country'} else results[1].split(" ")[2]
    elif any(match in result for match in win_loss_tie):
        win_loss=result[0]
        score=result[4:]
        if " " in score:
            split_score=score.split(" ", 1)
            score=split_score[0]
            reg_notes=split_score[1].lstrip()
            logging.info("Notes: {}".format(reg_notes))
        if reg_notes and len(reg_notes.split(" "))>2:
            split_notes=reg_notes.split(" ",2)
            reg_notes=" ".join(split_notes[:2])
            add_notes=split_notes[2]
        tech_score=int(score.split("-")[0])
        opponent_score=int(score.split("-")[1])
        if (win_loss=='W' and opponent_score>=tech_score) or (win_loss=='L' and opponent_score<=tech_score):
                opponent_score,tech_score=tech_score,opponent_score
    return win_loss,tech_score,opponent_score,reg_notes,add_notes

def nan_time_to_time(time):
    if time!=time:
        time="None"
    return time