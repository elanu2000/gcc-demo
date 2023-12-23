from flask import Flask, render_template, request, redirect, url_for
import uuid, json
import update_total_score
from threading import Thread

def read_rooms_from_file():
    try:
        with open('rooms.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_rooms_to_file(rooms):
    with open('rooms.json', 'w') as file:
        json.dump(rooms, file, indent=4)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    rooms = read_rooms_from_file()
    room_id = str(len(rooms) + 1)
    rooms[room_id] = {'players': []}
    write_rooms_to_file(rooms)
    return render_template('create_room.html', room_id=room_id)

@app.route('/finalize_room/<room_id>', methods=['POST'])
def finalize_room(room_id):
    players = request.form.getlist('players[]')
    rooms = read_rooms_from_file()
    if room_id in rooms:
        rooms[room_id]['players'] = players
        write_rooms_to_file(rooms)
        return redirect(url_for('room', room_id=room_id))
    else:
        return "Room not found", 404

@app.route('/room/<room_id>', methods=['GET'])
def room(room_id):
    rooms = read_rooms_from_file()
    if room_id in rooms:
        players = rooms[room_id].get('players', [])
        return render_template('room.html', players=players, room_id= room_id)
    else:
        return "Room not found", 404
    
# @app.route('/start_game/<room_id>', methods=['POST'])
# def start_game(room_id):
#     data = request.get_json()
#     home_team = data['home_team']
#     away_team = data['away_team']

#     update_total_score.start_game(home_team, away_team)
#     return json.jsonify({'message': 'Game has started'})

def start_game_thread(home_team, away_team):
    update_total_score.start_game(home_team, away_team)

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
        update_total_score.write_predictions(home_team, away_team, player_predictions)
        message_1 = "Game " + home_team + " - " + away_team + " is being processed!"
        message_2 = "Players: " + ", ".join(player_predictions)
    else:
        message_1 = "Game " + home_team + " - " + away_team + " is not being processed!"
        message_2 = "Players: " + ", ".join(player_predictions)

    return render_template('game_started.html', message_1 = message_1, message_2 = message_2)

if __name__ == '__main__':
    app.run(debug=True)
