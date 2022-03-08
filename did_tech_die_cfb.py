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
current_date = time.strptime("2021-09-04", "%Y-%m-%d") #testing
year = current_date.tm_year

def get_calendar_data():
    try:
        calendar_data = api_instance.get_calendar(year=year)
        return calendar_data
    except ApiException as e:
        print("Exception when calling GamesApi->get_calendar: %s\n" % e)

def get_game_week():
    calendar_data = get_calendar_data()
    #Iterate thru this year's football calendar
    for i in range(len(calendar_data)):
        #Assign the month, day, year of week's start and end date 
        start_date = time.strptime(calendar_data[i].first_game_start[:10], "%Y-%m-%d")
        end_date = time.strptime(calendar_data[i].last_game_start[:10], "%Y-%m-%d")
        #Check if current date is between week's start and end date
        if current_date >= start_date and current_date <= end_date:
            #If so, assign week & season_type from calendar
            week = calendar_data[i].week
            season_type = calendar_data[i].season_type
            return week, season_type

def get_game_data(week, season_type):
    try:
        # Games and results
        api_response = api_instance.get_games(year=year, week=week, season_type=season_type, team=team)
        game_data = api_response[0]
        return game_data
    except ApiException as e:
        print("Exception when calling CFBGamesApi->get_games: %s\n" % e)
    except IndexError as e:
        pass
        #print("Exception when calling CFBGamesApi->get_games: %s\n" % e)

def is_today_gameday(game_data):
    print("Checking if CFB gameday is today...")
    gameday = False
    game_start = time.strptime(game_data.start_date[:10], "%Y-%m-%d")
    if game_start != current_date:
        print("Tech CFB gameday is not today!")
    else:
        print("Tech CFB gameday is today!\n")
        gameday = True
    return gameday

def is_game_final(game_data):
    print("Checking if CFB game is final..")
    game_is_final = False
    #Score data is updated within minutes of a game being completed 
    if game_data.home_points and game_data.away_points:
        print("CFB game is final!\n")
        game_is_final = True
    else:
        print("CFB game is not final!")
    return game_is_final

def get_resulting_tweet(game_data):
    home_team = game_data.home_team
    away_team = game_data.away_team
    home_pts = str(game_data.home_points)
    away_pts = str(game_data.away_points)
    #Result(tweet): Yes/No from Tech W/L + sport emote + winning team & pts + losing team & pts
    if home_team == team:
        if home_pts > away_pts:
            result = "No.\n🏈: {} {}, {} {}".format(home_team, home_pts, away_team, away_pts)
        else:
            result = "Yes.\n🏈: {} {}, {} {}".format(away_team, away_pts, home_team, home_pts)
    else:
        if home_pts < away_pts:
            result = "No.\n🏈: {} {}, {} {}".format(away_team, away_pts, home_team, home_pts)
        else:
            result = "Yes.\n🏈: {} {}, {} {}".format(home_team, home_pts, away_team, away_pts)
    return result