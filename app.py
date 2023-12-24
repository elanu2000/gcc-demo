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
    players = request.form.getlist('players[]')
    room_id = utils.create_room(mongo_client, players)
    return redirect(url_for('room', room_id=room_id))

@app.route('/room/<room_id>', methods=['GET'])
def room(room_id):
    room = utils.get_room(mongo_client, room_id)
    if room:
        players = []
        for player_dict in room["players"]:
            players.append(player_dict["name"])
        return render_template('room.html', players=players, room_id= room_id)
    else:
        return "Room not found", 404

def start_game_thread(home_team, away_team):
    utils.start_game(home_team, away_team)

@app.route('/game_started', methods = ['POST'])
def game_started():
    room_id = request.form.get('room_id')
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    player_predictions = []
    for key, value in request.form.items():
        if key.startswith('player_input_'):
            player_predictions.append(value)

    thread = Thread(target=start_game_thread, args=(home_team, away_team))
    thread.start()
    if 0 not in player_predictions:
        utils.write_predictions(home_team, away_team, player_predictions)
        message_1 = "Game " + home_team + " - " + away_team + " is being processed!"
        message_2 = "Players: " + ", ".join(player_predictions)
    else:
        message_1 = "Game " + home_team + " - " + away_team + " is not being processed!"
        message_2 = "Players: " + ", ".join(player_predictions)

    return render_template('game_started.html', message_1 = message_1, message_2 = message_2)

if __name__ == '__main__':
    app.run(debug=True)
