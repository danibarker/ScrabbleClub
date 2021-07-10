import psycopg2 as db
import os
from datetime import datetime
import random
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


def get_players():
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT * from players""")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        players = select_to_object_array(rows, cols)
        return players
    except:
        return False


def open_event():
    try:
        day_of_the_week = datetime.today().weekday()
        query = f"INSERT INTO events (date,pairing_method) values ('{datetime.today()}', {2 if day_of_the_week == 3 else 1});"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
    except:

        cursor.execute("ROLLBACK")
        conn.commit()
    try:
        curs = conn.cursor()
        query = f"select * from events where date = '{datetime.today()}';"
        curs.execute(query)
        return curs.fetchone()[0]
    except:
        return False


def add_attendee(player_id, event_id):
    try:
        query = f"INSERT INTO event_attendees (player_id,event_id) values ({player_id}, {event_id});"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as err:
        print(err)
        cursor.execute("ROLLBACK")
        conn.commit()
        return False


def remove_attendee(player_id, event_id):
    try:
        query = f"DELETE FROM event_attendees WHERE player_id={player_id} AND event_id= ({event_id});"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as err:
        print(err)
        cursor.execute("ROLLBACK")
        conn.commit()
        return False


def select_to_object_array(rows, cols):
    array = []
    for row in rows:
        unit = {}
        for i, col in enumerate(row):
            unit[cols[i]] = col if not col == None else ""
        array.append(unit)
    return array


def get_attendees(event_id):
    day_of_the_week = datetime.today().weekday()
    try:
        query = f"""SELECT p.full_name, p.rating, p.rung 
        FROM event_attendees e 
        inner join players p on e.player_id = p.id 
        WHERE event_id= ({event_id}) 
        ORDER BY {'p.rung' if day_of_the_week == 3 else 'p.rating'};"""
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        attendees = select_to_object_array(rows, cols)

        return attendees
    except Exception as err:
        print(err)
        cursor.execute("ROLLBACK")
        conn.commit()
        return False


def set_byes(groups, num_of_byes, bye_group_number, event_id):
    try:
        cursor = conn.cursor()
        byes = random.sample(groups[bye_group_number], num_of_byes)
        for i, player in enumerate(byes):
            cursor.execute(f"""UPDATE event_attendees SET bye = {i+1}
            WHERE player_id = {player['id']} AND event_id = {event_id}""")
            conn.commit()
        return {"data": byes}
    except Exception as e:
        return {"error": e}


def set_player_groups(group, group_number, event_id):
    try:
        cursor = conn.cursor()
        cursor.execute(f'REPLACE INTO groups (event_id, group_number, round_number) \
        VALUES({event_id},{group_number},1)')
        conn.commit()
        group_id_query = cursor.execute(f'SELECT id FROM groups \
        WHERE event_id = {event_id} \
        AND group_number = {group_number}')
        group_id = group_id_query[0][0]
        for player in group:
            player_id = player['id']
            value_list = f'{group_id},{player_id},{event_id}'
            cursor.execute(f'REPLACE INTO \
            player_groups(group_id, player_id, event_id) \
            VALUES({value_list})')
            conn.commit()

    except Exception as e:
        return {"error": e}


def create_groups(event_id, given_byes=[]):
    players = get_attendees(event_id)
    num_players = len(players)
    number_of_groups = num_players // 4 + (1 if num_players % 4 == 3 else 0)
    distribution = num_players % 4

    group_sizes = [4 for _ in range(number_of_groups)]
    bye_group_number = random.randint(0, number_of_groups - 1)
    if distribution == 1:  # bye group has 5 players
        group_sizes[bye_group_number] = 5

    elif distribution == 2:  # no byes, group of 6
        group_sizes[random.randint(0, number_of_groups - 1)] = 6

    elif distribution == 3:  # bye group has 3 players

        group_sizes[bye_group_number] = 3

    elif num_players == 2:  # group of 2
        group_sizes = [2]
    else:  # all groups of 4
        pass
    groups = []

    for (i, k) in enumerate(group_sizes):
        group = players[:k]  #
        players = players[k:]  # Throw the first k out.
        groups.append(group)

    if distribution % 2 == 1:
        set_byes(groups, 3, bye_group_number, event_id)
    for i, group in enumerate(groups):
        group_number = i + 1
        set_player_groups(group, group_number, event_id)
    return groups


def start_event(event_id, given_byes=[]):
    day_of_the_week = datetime.today().weekday()
    players = get_attendees(event_id)
    if day_of_the_week == 3:
        return create_groups(event_id)
    else:
        set_player_groups(players, 1, event_id)
        if len(players) % 2 == 1:
            set_byes([players], 5, 1, event_id)
        return [players]


def add_result(event_id, round, group, player1, player2, score1, score2):
    cursor = conn.cursor()

    enter_result_query = f"""REPLACE INTO results (score_1, score_2, 
        player1, player2, round, group_id, event_id)
        VALUES ({score1},{score2},{player1},{player2},{round}, {group},{event_id});"""

    cursor.execute(enter_result_query)
    conn.commit()
