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

@app.route('/create_room', methods=['POST'])
def create_room():
    return render_template('create_room.html')

@app.route('/finalize_room', methods=['POST'])
def finalize_room():
    room_id = request.form.get('room_id')
    players = request.form.getlist('players[]')
    room_id = utils.create_room(mongo_client, players, room_id)
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

def start_game_thread(home_team, away_team):
    utils.start_game(home_team, away_team)

@app.route('/game_started', methods = ['POST'])
def game_started():
    room_id = request.form.get('room_id')
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    player_name = request.form['player']
    prediction = request.form['prediction']

    players = mongo_client.get_element("rooms", "room_id", room_id)["players"]
    
    for index, player_dict in enumerate(players):
        if player_dict["name"] == player_name:
            player_dict["prediction"] = prediction
        players[index] = player_dict
        
    mongo_client.update_document("rooms", "room_id", room_id, "players", players)

    is_prediction_complete = True
    player_predictions = []

    for player_dict in players:
        if player_dict["prediction"] == "0":
            is_prediction_complete = False
        player_predictions.append(str(player_dict["prediction"]))

    if is_prediction_complete:
        utils.write_predictions(home_team, away_team, player_predictions)
        thread = Thread(target=start_game_thread, args=(home_team, away_team))
        thread.start()
        message_1 = "Game " + home_team + " - " + away_team + " is being processed!"
        message_2 = "Players: " + ", ".join(player_predictions)
    else:
        message_1 = "Game " + home_team + " - " + away_team + " is not being processed!"
        message_2 = "Not all players have submitted!"

    return render_template('game_started.html', message_1 = message_1, message_2 = message_2)

if __name__ == '__main__':
    app.run(debug=True)
