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
cur = conn.cursor()
cur.execute("""END TRANSACTION;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS "players" CASCADE;
CREATE TABLE IF NOT EXISTS "players" (
	"id"	serial primary key,
	"first_name"	varchar(50),
	"last_name"	varchar(50),
	"discord"	varchar(50),
	"isc"	varchar(50),
	"abbreviation"	VARCHAR(50) DEFAULT NULL,
	"rating"	INTEGER,
	"rung"	INTEGER,
	"full_name"	VARCHAR(50) DEFAULT NULL,
	"current_opponent" INTEGER,
	FOREIGN KEY("current_opponent") REFERENCES "players"("id")
);
DROP TABLE IF EXISTS "pairing_methods" CASCADE;
CREATE TABLE IF NOT EXISTS "pairing_methods" (
	"id"	serial primary key,
	"name"	VARCHAR(50)
);

DROP TABLE IF EXISTS "events" CASCADE;
CREATE TABLE IF NOT EXISTS "events" (
	"id"	serial primary key,
	"date"	DATE UNIQUE,
	"pairing_method"	INTEGER,
	FOREIGN KEY("pairing_method") REFERENCES "pairing_methods"("id")
);
DROP TABLE IF EXISTS "groups" CASCADE;
CREATE TABLE IF NOT EXISTS "groups" (
	"id"	serial primary key,
	"event_id"	INTEGER,
	"group_number"	INTEGER,
	"round_number"	INTEGER,
	FOREIGN KEY("event_id") REFERENCES "events"("id")
);
DROP TABLE IF EXISTS "results";
CREATE TABLE IF NOT EXISTS "results" (
	"id"	serial primary key,
	"score_1"	INTEGER,
	"score_2"	INTEGER,
	"round"	INTEGER,
	"event_id"	INTEGER,
	"group_id"	INTEGER,
	"player1"	INTEGER,
	"player2"	INTEGER,
	UNIQUE("player1","player2","round"),
	FOREIGN KEY("event_id") REFERENCES "events"("id"),
	FOREIGN KEY("group_id") REFERENCES "groups"("id"),
	FOREIGN KEY("player2") REFERENCES "players"("id"),
	FOREIGN KEY("player1") REFERENCES "players"("id")
);
DROP TABLE IF EXISTS "event_attendees";
CREATE TABLE IF NOT EXISTS "event_attendees" (
	"id"	serial primary key,
	"player_id"	integer,
	"event_id"	integer,
	"bye"	boolean,
	UNIQUE("player_id","event_id"),
	FOREIGN KEY("event_id") REFERENCES "events"("id"),
	FOREIGN KEY("player_id") REFERENCES "players"("id")
);
DROP TABLE IF EXISTS "player_groups";
CREATE TABLE IF NOT EXISTS "player_groups" (
	"id"	serial primary key,
	"group_id"	INTEGER,
	"player_id"	INTEGER,
	"event_id"	INTEGER,
	UNIQUE("group_id","player_id"),
	FOREIGN KEY("player_id") REFERENCES "players"("id"),
	FOREIGN KEY("group_id") REFERENCES "groups"("id"),
	FOREIGN KEY("event_id") REFERENCES "events"("id")
);
INSERT INTO "players" ("id","first_name","last_name","discord","isc","abbreviation","rating","rung","full_name") VALUES (1,'Adam','Sivertson','ADAMS','','',500,NULL,'Adam Sivertson'),
 (2,'Albert','Hahn','ALBERTH','','',1778,NULL,'Albert Hahn'),
 (3,'Allan','Simon','niemand','NIEMAND','AS',1576,NULL,'Allan Simon'),
 (4,'Andrew','Shareski','ANDREWS','','',500,NULL,'Andrew Shareski'),
 (5,'Arthur','Milne','ARTHURM','','A2',818,NULL,'Arthur Milne'),
 (6,'Ava','Zeidler','AVAZ','','',418,NULL,'Ava Zeidler'),
 (7,'Betty','Bergeron','SHADFINN1','SHADFINN1','BB',1098,NULL,'Betty Bergeron'),
 (8,'Bobbi','Braden','BOBBIB','','B32',500,NULL,'Bobbi Braden'),
 (9,'Brendan','Huang','HEAVYMENTAL','KOIHASNOS','B22',1351,NULL,'Brendan Huang'),
 (10,'Carl','Madden','ZIZZ','MRENYGMA','CM3',1672,NULL,'Carl Madden'),
 (11,'Cheryl','Blum','CHERYLB','','',500,NULL,'Cheryl Blum'),
 (12,'Cheryl','Melvin','TILERACK','TILERACK','Cheryl Melvin',1296,NULL,'Cheryl Melvin'),
 (13,'Christopher','Rollins','CHRISR','','CRR',500,NULL,'Christopher Rollins'),
 (14,'Christopher','Sykes','TILERUNNER','TILERUNNER','C2',1866,NULL,'Christopher Sykes'),
 (15,'Danielle','Barker','DANIB','DANIB','DB2',940,NULL,'Danielle Barker'),
 (16,'David','Poder','jolie123','JOLIE123','David Poder',1764,NULL,'David Poder'),
 (17,'Dee','N','D4YYC','','',500,NULL,'Dee N'),
 (18,'Dorothy','Klovan','DOROTHYK','','D',624,NULL,'Dorothy Klovan'),
 (19,'Doug','Gilbert','DOUGG','','',500,NULL,'Doug Gilbert'),
 (20,'Emil','Rem','EMILR','','ER',1424,NULL,'Emil Rem'),
 (21,'Estelle','Matthews','ESTELLEM','','E',549,NULL,'Estelle Matthews'),
 (22,'Grace','Harris','GRACE47','GRACE47','G',958,NULL,'Grace Harris'),
 (23,'Jason','Krueger','JAYKRU','JFK','JK',1656,NULL,'Jason Krueger'),
 (24,'Jeff','Fleetham','JEFFF','','',1485,NULL,'Jeff Fleetham'),
 (25,'Juraj','Pivovarov','JURAJ','JURAJ','J5',1697,NULL,'Juraj Pivovarov'),
 (26,'Linda','Biegler','LINDAB','','LB3',500,NULL,'Linda Biegler'),
 (27,'Linda','Slater','Linda Slater','ALLEC2','LS',815,NULL,'Linda Slater'),
 (28,'Matt','Larocque','BACONATOR','BACONATOR','ML6',1741,NULL,'Matt Larocque'),
 (29,'Maureen','Clifford','MOTILES','MOTILES','MC2',1169,NULL,'Maureen Clifford'),
 (30,'Maureen','Morris','TRAVELGAL','TRAVELGAL','MM',1145,NULL,'Maureen Morris'),
 (31,'Nelly','Chow','NELLYC','','',500,NULL,'Nelly Chow'),
 (32,'Nicholas','Tam','QUIXOTICN','EPISTROPHY','NT',1500,NULL,'Nicholas Tam'),
 (33,'Noella','Ward','VAMPISH','VAMPISH','N',1398,NULL,'Noella Ward'),
 (34,'Peter','Maas','PETERM','','PM',1229,NULL,'Peter Maas'),
 (35,'Peter','Sargious','SUNGOER','SUNGOER','PS',1605,NULL,'Peter Sargious'),
 (36,'Randall','Thomas','RUNESMAN','RUNESMAN','R',1601,NULL,'Randall Thomas'),
 (37,'Richard','Martin','rhjmartin','RHJMARTIN','RM',1106,NULL,'Richard Martin'),
 (38,'Robyn','McKay','owlit','OWLIT','RM4',534,NULL,'Robyn McKay'),
 (39,'Rodney','Weis','TACTIX47','TACTIX47','R9',1081,NULL,'Rodney Weis'),
 (40,'Sally?','','SALLY','','',500,NULL,'Sally? '),
 (41,'Shiuli','Bawa','LILB','LILB','Shiuli Bawa',500,NULL,'Shiuli Bawa'),
 (42,'Siri','Tillekeratne','SIRIT','','ST',1466,NULL,'Siri Tillekeratne'),
 (43,'Stan','Hwang','chessimprov','CHESSIMP','Stan Hwang',994,NULL,'Stan Hwang'),
 (44,'Sue','Brigliadori','WURDWIZ','WURDWIZ','S2',1113,NULL,'Sue Brigliadori'),
 (46,'Terri','Morigeau','TERRI BELLE','TEBEMO','T',1073,NULL,'Terri Morigeau'),
 (47,'Terry','Aitken','TerryA','Travon','NPNPNP',1111,NULL,'Terry Aitken'),
 (48,'Tom','McKay','UNITOM','UNITOM','T8',407,NULL,'Tom McKay'),
 (49,'Vish','Wimalasena','VISHW','','',1343,NULL,'Vish Wimalasena'),
 (50,'Wayne','Clifford','LIKEABOSS','LIKEABOSS','W',1522,NULL,'Wayne Clifford'),
 (51,'Wendy','McGrath','wuffy','WUFFY','WM',1185,NULL,'Wendy McGrath'),
 (52,'Trish','McKay','liking','LIKING','Trish McKay',500,NULL,'Trish McKay'),
 (53,'Tanya','Lee','TANYAL','','',500,NULL,'Tanya Lee');
INSERT INTO "pairing_methods" ("id","name") VALUES (1,'Open 5 Rounds'),
 (2,'Ladder 3 Rounds');
COMMIT;


""")
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
    query = f"INSERT INTO events (date,pairing_method) values ('{datetime.today()}', {1 if day_of_the_week == 0 else 2})"
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
