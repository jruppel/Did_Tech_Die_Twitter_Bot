from __future__ import print_function
import calendar
from dataclasses import dataclass
import re
import time
from turtle import bye
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
all_bye_weeks = []

def get_calendar_data():
    try:
        calendar_data = api_instance.get_calendar(year=2019)
        return calendar_data
    except ApiException as e:
        print("Exception when calling GamesApi->get_calendar: %s\n" % e)

def get_game_week(calendar_data):
    #Iterate thru year calendar
    for i in range(len(calendar_data)):
        #Assign the month, day, year of week's start and end date 
        start_date = time.strptime(calendar_data[i].first_game_start[:10], "%Y-%m-%d")
        current_date = time.strptime("2019-12-20", "%Y-%m-%d") #testing
        end_date = time.strptime(calendar_data[i].last_game_start[:10], "%Y-%m-%d")
        #
        if current_date >= start_date and current_date <= end_date:
            week = calendar_data[i].week
            season_type = calendar_data[i].season_type
            return week, season_type
        
def get_total_games_played():
    try:
        # Team records
        api_response = api_instance.get_team_records(year=2019, team=team) #testing
        record_data = api_response[0]
        total_games = record_data.total["games"]
        return total_games
    except ApiException as e:
        print("Exception when calling GamesApi->get_team_records: %s\n" % e)

def get_total_weeks_played():
    game_week = get_game_week(get_calendar_data())
    total_weeks = games_played = get_total_games_played()
    bye_weeks = get_bye_weeks()
    for i in bye_weeks:
        if total_weeks >= i:
            total_weeks = total_weeks + 1
    if game_week[1] == 'postseason':
        total_weeks = total_weeks + 1
    return total_weeks

def get_game_data(week, season_type):
    try:
        # Games and results
        api_response = api_instance.get_games(year=2019, week=week, season_type=season_type, team=team) #testing
        game_data = api_response[0]
        return game_data
    except ApiException as e:
        print("Exception when calling CFBGamesApi->get_games: %s\n" % e)
    except IndexError as e:
        pass
        #print("Exception when calling CFBGamesApi->get_games: %s\n" % e)

#Determine how many bye weeks have happened up to the total games played
def get_bye_weeks():
    #Iterate thru total games played, game data starts at week 1
    for i in range(1, get_total_games_played()+1):
        #Bye weeks only happen during the regaular season
        week_data = get_game_data(i, "regular")
        #Each week in which game data does not exist is a bye
        if week_data == None:
            #Store previous week's number and add 1
            all_bye_weeks.append(get_game_data(i-1, "regular").week+1)
    return all_bye_weeks

def game_is_final():
    #final = False
    #if game_week == games_played:
    final = True
    #print(total_weeks)
    #print(game_week)
    #return final

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

#print(get_game_week(get_calendar_data()))
#game_is_final()
#print(get_result(get_game_data(1,"postseason")))
print(get_total_weeks_played())