import time, json
from MatchStatistics import MatchStatistics
from ExcelWriter import ExcelWriter
from MongoDb import MongoDb
from ExcelGenerator import ExcelGenerator
import ast, datetime

def get_total_score(match):
    teams = match.split("-")
    home_team = teams[0].strip()
    away_team = teams[1].strip()
    obj = MatchStatistics(home_team, away_team)
    obj.get_event_id()
    obj.get_goals()
    obj.get_total_corners()
    obj.get_adjusted_cards()
    return obj.get_total_score()

def start_game(home_team, away_team, spreadsheet_id):
    match_statistics = MatchStatistics(home_team, away_team)
    match = home_team + " - " + away_team
    excel_writer = ExcelWriter(spreadsheet_id)
    event_id = match_statistics.get_event_id()
    start_timestamp = match_statistics.get_start_timestamp(event_id)
    while time.time() < start_timestamp:
        print("Match has not started yet! It's starting at: " + datetime.datetime.fromtimestamp(start_timestamp).strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(180)
    is_match_finished = False
    while is_match_finished is False:
        print(match + ":")
        match_statistics.get_goals()
        match_statistics.get_total_corners()
        match_statistics.get_adjusted_cards()
        print(match_statistics.get_total_score())
        excel_writer.write_goals_corners_cards(match, match_statistics.total_goals, match_statistics.total_corners, match_statistics.total_adjusted_cards)
        if time.time() > start_timestamp + 6900 and match_statistics.is_match_finished():
            print("Match is finished!")
            is_match_finished = True
        else:
            time.sleep(180)

def write_predictions(home_team, away_team, players_input, room_id, spreadsheet_id):
    match = home_team + " - " + away_team
    excel_writer = ExcelWriter(spreadsheet_id)
    excel_writer.write_predictions(players_input, match)

def create_room(mongo_client, players, room_id):
    room = {"room_id" : room_id, "players" : {}}
    players_list = []
    for player in players:
        player_dict = {}
        player_dict["name"] = player
        # player_dict["prediction"] = "0"
        players_list.append(player_dict)
    room["players"] = players_list
    excel_writer = ExcelGenerator(room_id, players)
    room["spreadsheet_id"] = excel_writer.SPREADSHEET_ID
    room["matches"] = []
    print(room)
    mongo_client.write_element("rooms", room)

def get_room(mongo_client, room_id):
    return mongo_client.get_element("rooms", "room_id", room_id)

def string_to_list(string_list):
    try:
        # Safely evaluate the string as a Python expression
        result = ast.literal_eval(string_list)
        if isinstance(result, list):
            return result
        else:
            raise ValueError("The string does not represent a list.")
    except (ValueError, SyntaxError):
        return []