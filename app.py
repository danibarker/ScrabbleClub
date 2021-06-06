from flask import Flask
import requests
import psycopg2 as db

app = Flask(__name__)


@app.route('/db')
def test():
    print('here1')
    conn = db.connect(host='ec2-54-225-228-142.compute-1.amazonaws.com',
                      database='d3q0j784c29nfb',
                      user='kcxfpqbevmxdqj',
                      password='feb984d2b21b614016bfe616add870af8851999c3b40c9c761bff072f3e38ce2')
    print('here')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE vendors (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) NOT NULL
        )""")
    print('here2')
    cur.execute('SELECT * from vendors')
    rows = cur.fetchall()
    print('here3')
    print(rows)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/clubID/<club>')
def get_club(club):
    res = requests.post(
        'https://woogles.io/twirp/tournament_service.TournamentService/GetTournamentMetadata', json={"slug": f"/club/{club}"})
    text = res.json()
    return text


@app.route('/getGCG/<gameId>')
def get_gcg(gameId):
    res = requests.post(
        'https://woogles.io/twirp/game_service.GameMetadataService/GetGCG', json={"gameId": gameId})
    text = res.json()
    f = open(f'static/{gameId}.gcg', 'w')
    f.write(text['gcg'])
    f.close()
    return app.send_static_file(f'{gameId}.gcg')


@app.route('/recentGames/<clubID>/<page>')
def recent_games(clubID, page):
    print('here')
    res = requests.post('https://woogles.io/twirp/tournament_service.TournamentService/RecentGames',
                        json={"id": clubID, "num_games": 20, "offset": 20*int(page)-1})
    text = res.json()
    return text


if __name__ == '__main__':
    test()
    app.run()
