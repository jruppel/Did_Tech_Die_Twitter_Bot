from __future__ import print_function
import calendar
from dataclasses import dataclass
import re
import time
from turtle import bye
from webbrowser import get
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
#current_date = time.gmtime()
current_date = time.strptime("2019-09-01", "%Y-%m-%d")
year = current_date.tm_year
final = False
all_bye_weeks = []

def get_calendar_data():
    try:
        calendar_data = api_instance.get_calendar(year=2019)
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
        api_response = api_instance.get_games(year=2019, week=week, season_type=season_type, team=team)
        game_data = api_response[0]
        return game_data
    except ApiException as e:
        print("Exception when calling CFBGamesApi->get_games: %s\n" % e)
    except IndexError as e:
        pass
        #print("Exception when calling CFBGamesApi->get_games: %s\n" % e)

def is_today_gameday():
    gameday = False
    game_week = get_game_week()
    game_data = get_game_data(game_week[0], game_week[1])
    if game_data == None:
        print("Tech is on a bye week!")
    else:
        game_start = time.strptime(game_data.start_date[:10], "%Y-%m-%d")
        if game_start != current_date:
            print("Tech gameday is not today!")
        else:
            print("Tech gameday is today!")
            gameday = True
    return gameday

#Determine how many bye weeks have happened up to the total games played
def get_bye_weeks():
    #Iterate thru total games played, game data starts at week 1
    #Todo: get range of regular season
    for i in range(1, 16):
        #Bye weeks only happen during the regaular season
        week_data = get_game_data(i, "regular")
        #Each week in which there is no game data is a bye
        if week_data == None:
            #Store previous week's number and add 1
            all_bye_weeks.append(get_game_data(i-1, "regular").week+1)
    return all_bye_weeks

def get_total_weeks_played():
    game_week = get_game_week()
    total_weeks = game_week[0]
    if game_week[1] == 'postseason':
        #Postseason is week 16
        total_weeks = total_weeks + 15     
    return total_weeks

#factor in get_bye_weeks data in total games(?)
def get_total_games_played():
    total_weeks = total_games = get_total_weeks_played()
    for i in range(1, total_weeks+1):
        #Get all regular season game data
        game_data = get_game_data(i, "regular")
        #Get postseason data if week 16
        if i == 16:
            game_data = get_game_data(1, "postseason")
        #Game data exists with final scores
        if game_data == None or game_data.home_points == None or game_data.away_points == None:
            total_games = total_games - 1
    return total_games

def game_is_final():
    print("Checking if game is final.")
    game_is_final = final
    bye_weeks = get_bye_weeks()
    total_weeks = get_total_weeks_played()
    total_games_and_byes = get_total_games_played()
    if total_weeks in bye_weeks:
        print("Tech is in a bye week. No final score this week.")
    for i in bye_weeks:
    #    if total_weeks == i:
    #        print("Tech is in a bye week. No final score this week.")
        if total_weeks > i:
            #print("After Bye Week: " + str(i))
            total_games_and_byes = total_games_and_byes + bye_weeks.count(i)
    if total_games_and_byes == total_weeks:
        print("Game is final!")
        game_is_final = True
    else:
        print("Game is not final!")
    return game_is_final

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

#print(get_total_weeks_played())
#print(get_total_games_played())
#print(game_is_final())
#print(get_game_data(1, 'regular'))
