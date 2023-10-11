# Game Info
import constants

logging,boxscore_sports,no_boxscore_sports=constants.logging,constants.boxscore_sports,constants.no_boxscore_sports

def is_game_exhibition(opponent):
    exhibition=False
    if "(exhibition)" in opponent:
        exhibition=True
        logging.info("This Tech game is an exhibition; no tweet needed!")
    else:
        logging.info("This Tech game is not an exhibition!")
    return exhibition

def is_game_final(result):
    final=False
    if not result!=result and result not in {None,'Canceled','Postponed'}:
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


def result_to_score(sport,result):
    reg_notes=add_notes=""
    if sport in boxscore_sports:
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
    elif sport in no_boxscore_sports:
        win_loss=opponent_score=None
        if sport in {'womens-bowling','mens-golf'}:
            tech_score=result
        if sport in {'mens-track-and-field','womens-track-and-field','mens-cross-country','womens-cross-country'}:
            results=result.split(';')
            if sport in {'mens-track-and-field','mens-cross-country'}:
                tech_score=results[0].split(" ")[1]
            if sport in {'womens-track-and-field','womens-cross-country'}:
                tech_score=results[1].split(" ")[2]
    return win_loss,tech_score,opponent_score,reg_notes,add_notes

def nan_time_to_time(time):
    if time!=time:
        time="None"
    return time

def get_team_sport(sport):
    if sport=='football':
        team_sport="🏈:"
    elif sport=='mens-basketball':
        team_sport="Men's 🏀:"
    elif sport=='womens-basketball':
        team_sport="Women's 🏀:"
    elif sport=="baseball":
        team_sport="⚾:"
    elif sport=="softball":
        team_sport="🥎:"
    elif sport=="womens-soccer":
        team_sport="⚽:"
    elif sport=='womens-volleyball':
        team_sport="🏐:"
    elif sport=='womens-tennis':
        team_sport="🎾:"
    elif sport=='mens-golf':
        team_sport="⛳:"
    elif sport=="womens-bowling":
        team_sport="🎳:"
    elif sport=="mens-track-and-field":
        team_sport="Men's T&F 🏃:"
    elif sport=="womens-track-and-field":
        team_sport="Women's T&F 🏃:"
    elif sport=="mens-cross-country":
        team_sport="Men's XC 🏃:"
    elif sport=="womens-cross-country":
        team_sport="Women's XC 🏃:"
    return team_sport