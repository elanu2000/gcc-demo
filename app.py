from flask import Flask, render_template, request, redirect, url_for
import uuid, json
import utils
from threading import Thread
from MongoDb import MongoDb

app = Flask(__name__)
mongo_client = MongoDb()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/create_room/<room_id>', methods=['GET'])
def create_room(room_id):
    if utils.get_room(mongo_client, room_id) is None:
        return render_template('create_room.html', room_id=room_id)
    return render_template("error.html", error="Room already exists!")

@app.route('/finalize_room', methods=['POST'])
def finalize_room():
    room_id = request.form.get('room_id')
    players = request.form.getlist('players[]')
    utils.create_room(mongo_client, players, room_id)
    return redirect(url_for('room', room_id=room_id))

@app.route('/room/<room_id>', methods=['GET'])
def room(room_id):
    room = utils.get_room(mongo_client, room_id)
    if room:
        players = []
        for player_dict in room["players"]:
            players.append(player_dict["name"])
        print(players)
        return render_template('room.html', players=players, room_id= room_id)
    else:
        return "Room not found", 404
    
@app.route('/room/<room_id>/<match>', methods=['POST'])
def select_match(room_id, match):
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    players_string = request.form.get('players')
    players = utils.string_to_list(players_string)
    print(players)
    return render_template('make_prediction.html', room_id=room_id, home_team=home_team, away_team=away_team, players=players)

def start_game_thread(home_team, away_team, spreadsheet_id):
    utils.start_game(home_team, away_team, spreadsheet_id)

@app.route('/game_started', methods = ['POST'])
def game_started():
    room_id = request.form.get('room_id')
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    player_name = request.form['player']
    prediction = request.form['prediction']

    players = mongo_client.get_element("rooms", "room_id", room_id)["players"]
    room_matches = mongo_client.get_element("rooms", "room_id", room_id)["matches"]
    match_document = mongo_client.get_element_by_query("matches", {"home_team": home_team, "away_team": away_team})

    if match_document is None:
        match_document = {"home_team": home_team, "away_team": away_team, "rooms": []}
        mongo_client.write_element("matches", match_document)
    
    match_document_rooms = match_document["rooms"]
    predictions = []

    is_room_in_matches = False
    for room_index, room_dict in enumerate(match_document_rooms):
        if room_dict["room_id"] == room_id:
            is_room_in_matches = True
            predictions = room_dict["predictions"]
            for index, player_dict in enumerate(predictions):
                if player_dict["name"] == player_name:
                    player_dict["prediction"] = prediction
                predictions[index] = player_dict
            room_dict["predictions"] = predictions
            match_document_rooms[room_index] = room_dict
    
    if is_room_in_matches is False:
        room_dict = {"room_id": room_id, "predictions": []}
        for player_dict in players:
            if player_dict["name"] == player_name:
                predictions.append({"name": player_dict["name"], "prediction": prediction})
            else:
                predictions.append({"name": player_dict["name"], "prediction": 0})
        room_dict["predictions"] = predictions
        match_document_rooms.append(room_dict)

    mongo_client.update_document_by_query("matches", {"home_team": home_team, "away_team": away_team}, {"rooms": match_document_rooms})
        

    # for index, player_dict in enumerate(players):
    #     if player_dict["name"] == player_name:
    #         player_dict["prediction"] = prediction
    #     players[index] = player_dict

    is_match_in_room = False

    for match_dict in room_matches:
        if match_dict["home_team"] == home_team and match_dict["away_team"] == away_team and match_dict["is_finished"] == False:
            is_match_in_room = True

    if is_match_in_room is False:
        match = {
            "home_team": home_team,
            "away_team": away_team,
            "is_finished": False
        }
        room_matches.append(match)
        mongo_client.update_document("rooms", "room_id", room_id, "matches", room_matches)
        
    mongo_client.update_document("rooms", "room_id", room_id, "players", players)

    is_prediction_complete = True
    player_predictions = []

    for player_dict in predictions:
        if player_dict["prediction"] == "0" or player_dict["prediction"] == 0:
            is_prediction_complete = False
        player_predictions.append(str(player_dict["prediction"]))

    if is_prediction_complete:
        spreadsheet_id = mongo_client.get_element("rooms", "room_id", room_id)["spreadsheet_id"]
        utils.write_predictions(home_team, away_team, predictions, room_id, spreadsheet_id)
        thread = Thread(target=start_game_thread, args=(home_team, away_team, spreadsheet_id))
        thread.start()
        message_1 = "Game " + home_team + " - " + away_team + " is being processed!"
        message_2 = "Players: " + ", ".join(player_predictions)
        message_3 = "https://docs.google.com/spreadsheets/d/" + spreadsheet_id
    else:
        message_1 = "Game " + home_team + " - " + away_team + " is not being processed!"
        message_2 = "Not all players have submitted!"
        message_3 = ""

    return render_template('game_started.html', message_1 = message_1, message_2 = message_2, message_3 = message_3)

if __name__ == '__main__':
    app.run(debug=True)
