from __future__ import print_function
import calendar
import re
import time
import cfbd
from cfbd.rest import ApiException
from pprint import pprint
import constants

# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = constants.cfbd_api_key
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
configuration.api_key_prefix['Authorization'] = 'Bearer'
# create an instance of the API class
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
team = 'Louisiana Tech'
current_date = time.gmtime()
year = current_date.tm_year

def get_calendar_data():
    try:
        calendar_data = api_instance.get_calendar(year=year)
        return calendar_data
    except ApiException as e:
        print("Exception when calling GamesApi->get_calendar: %s\n" % e)

def get_game_week(calendar_data):
    for i in range(len(calendar_data)-1):
        start_date = time.strptime(calendar_data[i].first_game_start[:10], "%Y-%m-%d")
        current_date = time.strptime("2021-09-30", "%Y-%m-%d")
        end_date = time.strptime(calendar_data[i+1].first_game_start[:10], "%Y-%m-%d")
        if current_date >= start_date and current_date < end_date:
            week = calendar_data[i].week
            season_type = calendar_data[i].season_type
            return week, season_type


def get_total_games():
    try:
        # Team records
        api_response = api_instance.get_team_records(year=year, team=team)
        record_data = api_response[0]
        total_games = record_data.total["games"]
        return total_games
    except ApiException as e:
        print("Exception when calling GamesApi->get_team_records: %s\n" % e)

def get_game_data(week, season_type):
    try:
        # Games and results
        api_response = api_instance.get_games(year=year, week=week, season_type=season_type, team=team)
        game_data = api_response[0]
        return game_data
    except ApiException as e:
        print("Exception when calling CFBGamesApi->get_games: %s\n" % e)
    except IndexError as e:
        print("Exception when calling CFBGamesApi->get_games: %s\n" % e)


def get_result(game_data):
    if game_data.home_team == "Louisiana Tech":
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

#print(get_game_week(get_calendar_data(2021)))