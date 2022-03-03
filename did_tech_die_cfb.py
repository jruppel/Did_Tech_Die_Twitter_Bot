from __future__ import print_function
import time
import cfbd
from cfbd.rest import ApiException
import constants

# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = constants.cfbd_api_key
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
configuration.api_key_prefix['Authorization'] = 'Bearer'
# create an instance of the API class
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
team = 'Louisiana Tech'
#current_date = time.gmtime()
current_date = time.strptime("2021-09-18", "%Y-%m-%d")
year = current_date.tm_year

def get_calendar_data():
    try:
        calendar_data = api_instance.get_calendar(year=2021)
        return calendar_data
    except ApiException as e:
        print("Exception when calling GamesApi->get_calendar: %s\n" % e)

def get_game_week():
    calendar_data = get_calendar_data()
    #Iterate thru year calendar
    for i in range(len(calendar_data)):
        #Assign the month, day, year of week's start and end date 
        start_date = time.strptime(calendar_data[i].first_game_start[:10], "%Y-%m-%d")
        end_date = time.strptime(calendar_data[i].last_game_start[:10], "%Y-%m-%d")
        #
        if current_date >= start_date and current_date <= end_date:
            week = calendar_data[i].week
            season_type = calendar_data[i].season_type
            return week, season_type

def get_game_data(week, season_type):
    try:
        # Games and results
        api_response = api_instance.get_games(year=2021, week=week, season_type=season_type, team=team)
        game_data = api_response[0]
        return game_data
    except ApiException as e:
        print("Exception when calling CFBGamesApi->get_games: %s\n" % e)
    except IndexError as e:
        pass
        #print("Exception when calling CFBGamesApi->get_games: %s\n" % e)

def is_today_gameday(game_data):
    print("Checking if gameday is today")
    gameday = False
    if game_data == None:
        print("Tech is on a bye week")
    else:
        game_start = time.strptime(game_data.start_date[:10], "%Y-%m-%d")
        if game_start != current_date:
            print("Tech gameday is not today")
        else:
            print("Tech gameday is today!")
            gameday = True
    return gameday

def game_is_final(game_data):
    print("Checking if game is final")
    game_is_final = False
    if game_data.home_points and game_data.away_points:
        print("Game is final")
        game_is_final = True
    else:
        print("Game is not final")
    return game_is_final

def get_result(game_data):
    if game_data.home_team == team:
        if game_data.home_points > game_data.away_points:
            result = 'W'
        else:
            result = 'L'
    else:
        if game_data.home_points < game_data.away_points:
            result = 'W'
        else:
            result = 'L'
    return result

#print(get_total_weeks_played())
#print(get_total_games_played())
#print(game_is_final())
#print(get_game_data(1, 'regular'))
