from flask import Flask, send_from_directory
import requests
import psycopg2 as db
import os
from datetime import datetime

# Set environment variables
if not os.environ.get('HEROKU'):

    os.environ['host'] = 'localhost'
    os.environ['database'] = 'scrabble'
    os.environ['user'] = 'danielle'
    os.environ['password'] = 'password'

# Get environment variables
USER = os.getenv('user')
PASSWORD = os.environ.get('password')
DATABASE = os.environ.get('database')
HOST = os.environ.get('host')
conn = db.connect(host=HOST,
                      database=DATABASE,
                      user=USER,
                      password=PASSWORD)
app = Flask(__name__,static_folder="./client/build")

# @app.route('/')
# def index():
#     return app.send_static_file('index.html')

@app.route('/get_players')
def get_players():
    
    cur = conn.cursor()
    cur.execute("""SELECT * from players""")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    print(cols)
    players = []
    for row in rows:
        player = {}
        for i,col in enumerate(row):
            player[cols[i]] = col
        players.append(player)

    return str(players)

@app.route('/start-event')
def start_event():
    day_of_the_week = datetime.today().weekday()
    query = f"INSERT INTO events (date,pairing_method) values ('{datetime.today()}', {2 if day_of_the_week == 3 else 1})"
    cur = conn.cursor()
    cur.execute(query)
    return 'event open'


@app.route('/club-id/<club>')
def get_club(club):
    res = requests.post(
        'https://woogles.io/twirp/tournament_service.TournamentService/GetTournamentMetadata', json={"slug": f"/club/{club}"})
    text = res.json()
    return text


@app.route('/get-GCG/<gameId>')
def get_gcg(gameId):
    res = requests.post(
        'https://woogles.io/twirp/game_service.GameMetadataService/GetGCG', json={"gameId": gameId})
    text = res.json()
    f = open(f'static/{gameId}.gcg', 'w')
    f.write(text['gcg'])
    f.close()
    return app.send_static_file(f'{gameId}.gcg')


@app.route('/recent-games/<clubID>/<page>')
def recent_games(clubID, page):
    print('here')
    res = requests.post('https://woogles.io/twirp/tournament_service.TournamentService/RecentGames',
                        json={"id": clubID, "num_games": 20, "offset": 20*(int(page)-1)})
    text = res.json()
    return text
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
