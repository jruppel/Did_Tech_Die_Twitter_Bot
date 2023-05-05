# Game Info
import constants

logging=constants.logging

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

def result_to_score(sport, result):
    if sport in {'Baseball', 'Womens-soccer', 'Softball', 'Womens-volleyball', 'Football', 'Mens-basketball', 'Womens-basketball', 'Womens-tennis'}:
        win_loss = result[0]
        score = result[4:]
        reg_notes = ""
        add_notes = ""
        if " " in score:
            split_score = score.split(" ", 1)
            score = split_score[0]
            reg_notes = split_score[1]
            logging.info("Notes: {}".format(reg_notes))
        if reg_notes and len(reg_notes.split(" ")) > 2:
            split_notes = reg_notes.split(" ", 2)
            reg_notes = " ".join(split_notes[:2])
            add_notes = split_notes[2]
        tech_score = int(score.split("-")[0])
        opponent_score = int(score.split("-")[1])
        if (win_loss == 'W' and opponent_score >= tech_score) or (win_loss == 'L' and opponent_score <= tech_score):
                opponent_score,tech_score=tech_score,opponent_score
    if sport in {'Womens-bowling', 'Mens-golf', 'Mens-track-and-field', 'Womens-track-and-field', 'Mens-cross-country', 'Womens-cross-country'}:
        win_loss = opponent_score = None
        if sport in {'Womens-bowling', 'Mens-golf'}:
            tech_score = result
        if sport in {'Mens-track-and-field', 'Womens-track-and-field', 'Mens-cross-country', 'Womens-cross-country'}:
            results = result.split(';')
            if sport in {'Mens-track-and-field', 'Mens-cross-country'}:
                tech_score = results[0].split(" ")[1]
            if sport in {'Womens-track-and-field', 'Womens-cross-country'}:
                tech_score = results[1].split(" ")[2]
    return win_loss, tech_score, opponent_score, reg_notes, add_notes

def nan_time_to_time(time):
    if time!=time:
        time="None"
    return time

def get_team_sport(sport):
    if sport=='Football':
        team_sport="🏈:"
    elif sport=='Mens-basketball':
        team_sport="Men's 🏀:"
    elif sport=='Womens-basketball':
        team_sport="Women's 🏀:"
    elif sport=="Baseball":
        team_sport="⚾:"
    elif sport=="Softball":
        team_sport="🥎:"
    elif sport=="Womens-soccer":
        team_sport="⚽:"
    elif sport=='Womens-volleyball':
        team_sport="🏐:"
    elif sport=='Womens-tennis':
        team_sport="🎾:"
    elif sport=='Mens-golf':
        team_sport="⛳:"
    elif sport=="Womens-bowling":
        team_sport="🎳:"
    elif sport=="Mens-track-and-field":
        team_sport="Men's T&F 🏃:"
    elif sport=="Womens-track-and-field":
        team_sport="Women's T&F 🏃:"
    elif sport=="Mens-cross-country":
        team_sport="Men's XC 🏃:"
    elif sport=="Womens-cross-country":
        team_sport="Women's XC 🏃:"
    return team_sport