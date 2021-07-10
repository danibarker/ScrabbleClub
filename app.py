from flask import Flask, send_from_directory
import requests
from db import add_result, get_attendees, \
    get_players, open_event, add_attendee, \
    remove_attendee, start_event
import os

app = Flask(__name__, static_folder="./client/build")


@app.route('/get_players')
def get_players_route():

    players = get_players()

    return {"error": "" if players else "failed to get", "data": str(players)}


@app.route('/open-event')
def open_event_route():
    event_id = open_event()
    return {"error": "" if event_id else "failed to open", "data": event_id}


@app.route('/add-attendee/<event_id>/<player_id>')
def add_attendee_route(event_id, player_id):
    added = add_attendee(event_id, player_id)
    return {"error": "" if added else "failed to add"}


@app.route('/remove-attendee/<event_id>/<player_id>')
def remove_attendee_route(event_id, player_id):
    removed = remove_attendee(event_id, player_id)
    return {"error": "" if removed else "failed to remove"}


@app.route('/get-attendees/<event_id>')
def get_attendees_route(event_id):
    attendees = get_attendees(event_id)
    return {"error": "" if attendees else "failed to get", "data": str(attendees)}


@app.route('/club-id/<club>')
def get_club_route(club):
    try:
        res = requests.post(
            'https://woogles.io/twirp/tournament_service.TournamentService/GetTournamentMetadata', json={"slug": f"/club/{club}"})
        text = res.json()
        return {"data": text}
    except Exception as e:
        return {"error": e}


@app.route('/get-GCG/<gameId>')
def get_gcg_route(gameId):
    try:
        res = requests.post(
            'https://woogles.io/twirp/game_service.GameMetadataService/GetGCG', json={"gameId": gameId})
        text = res.json()
        f = open(f'static/{gameId}.gcg', 'w')
        f.write(text['gcg'])
        f.close()
        return {"data": app.send_static_file(f'{gameId}.gcg')}
    except Exception as e:
        return {"error": e}


@app.route('/recent-games/<clubID>/<page>')
def recent_games_route(clubID, page):
    try:
        res = requests.post('https://woogles.io/twirp/tournament_service.TournamentService/RecentGames',
                            json={"id": clubID, "num_games": 20, "offset": 20*(int(page)-1)})
        text = res.json()
        return {"data": text}
    except Exception as e:
        return {"error": e}


@app.route('/start-event/<event_id>')
def start_event_route(event_id):
    return str(start_event(event_id))


@app.route('/add-result/<event_id>/<round>/<group>/<player1>/<player2>/<score1>/<score2>')
def add_result_route(event_id, round, group, player1, player2, score1, score2):
    add_result(event_id, round, group, player1, player2, score1, score2)


@app.route('/get-pairings/<event_id>/<group>')
def get_pairings_route(event_id, group):
    pairings = get_pairings(event_id, group)
    return pairings


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    print(path)
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run()
