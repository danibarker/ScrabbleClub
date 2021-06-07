from datetime import datetime
import networkx as nx
from itertools import combinations
from db import conn, get_attendees, select_to_object_array
class ScoreCard:
        def __init__(self):
            self.id = ""  # 0
            self.winscore = 0  # 1
            self.winoppscore = 0  # 2
            self.losescore = 0  # 3
            self.loseoppscore = 0  # 4
            self.spread = 0  # 5
            self.wins = 0.0  # 6
            self.games = 0  # 8
            self.highgame = 0  # 9
            self.losses = 0.0

def get_scorecards(group_id, player_group):
    # CALCULATES SPREADS, TOTALS, AVERAGE and HIGH SCORE and SORTS BY GROUP,WINS,SPREAD

    cursor = conn.cursor()
    rows = cursor.execute(f"""SELECT r.* FROM results r
    INNER JOIN groups g on r.group_id = g.id
    WHERE g.id = {group_id}""")
    cols = [desc[0] for desc in cursor.description]
    results = select_to_object_array(rows,cols)
    cards = []
    for x in player_group:
        card = ScoreCard()
        card.id = x['id']
        card.player = x
        cards.append(card)

    cards_by_id = dict([(x.id, x) for x in cards])
    # stereo = store the results twice, once for A vs B, and once for B vs A
    
    stereo = [[a.player1, a.score_1, a.player2, a.score_2] for a in results]
    stereo += [[a.player2, a.score_2, a.player1, a.score_1] for a in results]
    for r in stereo:
        # r = ['RANDAL', '346', 'JURAJPI', '345', '1', '1']
        [p1, s1, _p2, s2] = r
        # Always only update p1's card.
        card = cards_by_id.get(p1)
        if card:
            card.highgame = max(card.highgame, s1)
            card.games += 1
            if s1 > s2:
                # p1 wins
                card.winscore += s1
                card.winoppscore += s2
                card.wins += 1
            elif s1 == s2:
                # p1 p2 tie
                card.winscore += s1  # Make sure ties don't affect average scores.
                card.winoppscore += s2
                card.wins += 0.5
                card.losses += 0.5
            else:
                # p1 loses.
                card.losescore += s1
                card.loseoppscore += s2
                card.wins += 0
                card.losses += 1

            card.spread += s1 - s2
    return cards


def get_pairings(group_id, round_number):
    cursor = conn.cursor()
    day_of_the_week = datetime.today().weekday()
    rows = cursor.execute(f"""SELECT p.*, FROM player_groups pg 
    INNER JOIN players p ON p.id = pg.player_id
    WHERE pg.id = {group_id} ORDER BY 
    {'p.rung' if day_of_the_week == 3 else 'p.rating'}""")

    cols = [desc[0] for desc in cursor.description]
    player_group = select_to_object_array(rows,cols)
    round_number = player_group[0]['round_number']
    scorecards = get_scorecards(group_id, player_group)


    if round_number <= 1:
        pairs = pairings_swiss(player_group)
    elif round_number <= 4:
        pairs = pairings_koth(player_group, scorecards, avoid_repeats=True)
    else:
        pairs = pairings_koth(player_group, scorecards, avoid_repeats=False)

    return pairs


def pairings_koth(player_group, scorecards, avoid_repeats=True):
    past_matches = {}
    players_list = {}
    network = nx.Graph()
    for player in player_group:
        for match in player['played_with']:
            try:
                past_matches[match + player.name] += 1
                past_matches[player.name + match] += 1
            except KeyError:
                past_matches[match + player.name] = 1
                past_matches[player.name + match] = 1

    correction = len(scorecards) + 1
    for sc in scorecards:
        correction -= 1
        try:
            if byes[round_number - 1].name != sc.id:
                players_list[sc.id] = [sc.wins, sc.spread, correction]
        except IndexError:
            players_list[sc.id] = [sc.wins, sc.spread, correction]

    for (p1, p2) in combinations(players_list, 2):
        player_1_win_spread = players_list[p1][0] * 10000 + players_list[p1][1]
        player_2_win_spread = players_list[p2][0] * 10000 + players_list[p2][1]
        try:
            played_together = -1000000.0 * past_matches[p1 + p2]
        except KeyError:
            played_together = 0

        # do not worry about having played together or not, straight KOTH
        if not avoid_repeats:
            played_together = 0

        adjustment = players_list[p1][2] * (players_list[p1][2] - players_list[p2][2])
        weight_value = played_together - adjustment * (abs(player_2_win_spread - player_1_win_spread)) + 50000000
        if p1 != 'BYE' and p2 != 'BYE':
            network.add_edge(p1, p2, weight=weight_value)
    result = nx.algorithms.max_weight_matching(network, maxcardinality=True)
    return result


def pairings_swiss(player_group):
    # This is hardcoded to assume swiss pairings will only be used for the first round.
    # it simply chops the list in two [A1..An] and [B1..Bn], by rating where 
    # the A's are the top half and the B's are the bottom half.
    # It then pairs A1 vs B1, A2 vs B2, ..., An vs Bn.


    # Find all players but the bye, if there is  one.
    if byes:
        attendees = [x for x in player_group if x != byes[0]]
    else:
        attendees = player_group

    # Since we have taken out the byes, the list should be even now.

    assert len(attendees) % 2 == 0

    n = len(attendees) // 2

    part1 = attendees[:n]  # Top half
    part2 = attendees[n:]  # Bottom half

    pairs = []
    for (p1, p2) in zip(part1, part2):
        pairs.append((p1.name, p2.name))

    return pairs
