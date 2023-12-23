import time, json
from MatchStatistics import MatchStatistics
from ExcelWriter import ExcelWriter

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

def start_game(home_team, away_team):
    match_statistics = MatchStatistics(home_team, away_team)
    match = home_team + " - " + away_team
    excel_writer = ExcelWriter(match)
    event_id = match_statistics.get_event_id()
    start_timestamp = match_statistics.get_start_timestamp(event_id)
    while time.time() < start_timestamp:
        time.sleep(180)
    is_match_finished = False
    while is_match_finished is False:
        if time.time() > start_timestamp + 6900 and match_statistics.is_match_finished():
            print("Match is finished!")
            is_match_finished = True
        print(match + ":")
        match_statistics.get_goals()
        match_statistics.get_total_corners()
        match_statistics.get_adjusted_cards()
        print(match_statistics.get_total_score())
        excel_writer.write_goals_corners_cards(match_statistics.total_goals, match_statistics.total_corners, match_statistics.total_adjusted_cards)
        time.sleep(180)

def write_predictions(home_team, away_team, predictions):
    match = home_team + " - " + away_team
    excel_writer = ExcelWriter(match)
    excel_writer.write_predictions(predictions)