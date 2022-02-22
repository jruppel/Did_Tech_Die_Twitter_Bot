from __future__ import print_function
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

def get_record(year):
    try:
        # Team records
        api_response = api_instance.get_team_records(year=year, team=team)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling GamesApi->get_team_records: %s\n" % e)

def get_game_data(year, week, season_type):
    try:
        # Games and results
        api_response = api_instance.get_games(year, week, season_type, team)
        game_data = api_response[0]
        pprint(game_data)
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