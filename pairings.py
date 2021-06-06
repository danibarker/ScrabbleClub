import networkx as nx
from itertools import combinations


def get_pairings_text(current_round_number, scorecards, _players, _byes, _group=False, _bye_group=False):
    global round_number, cards, players, byes, group, bye_group
    round_number = current_round_number
    cards = scorecards
    players = _players
    byes = _byes
    bye_group = _bye_group
    group = _group

    if round_number <= 1:
        if group:
            pairs = pairings_group_round1()
        else:
            pairs = pairings_swiss()
    elif round_number <= 4:
        pairs = pairings_koth(avoid_repeats=True)
    else:
        pairs = pairings_koth(avoid_repeats=False)

    header = f"ROUND {round_number}"
    for pair in pairs:
        p1 = [p for p in players if p.name == pair[0]][0]
        p2 = [p for p in players if p.name == pair[1]][0]
        p1.current_opponent = p2.isc
        p2.current_opponent = p1.isc
    body = format_pairings(pairs)
    text = header + "\n" + body
    if group:
        text = body
    return text


def pairings_group_round1():
    players_in_group = [p for p in players if (p != byes[0] if byes else True)]
    num_pairs = len(players_in_group) // 2
    pairs = []
    for p in range(num_pairs):
        pairs.append((players_in_group[2 * p].name, players_in_group[2 * p + 1].name))
    return pairs


def pairings_koth(avoid_repeats=True):
    past_matches = {}
    players_list = {}
    network = nx.Graph()
    for player in players:
        for match in player.played_with:
            try:
                past_matches[match + player.name] += 1
                past_matches[player.name + match] += 1
            except KeyError:
                past_matches[match + player.name] = 1
                past_matches[player.name + match] = 1

    correction = len(cards) + 1
    for sc in cards:
        correction -= 1
        if sc.player in players:
            try:
                if byes[round_number - 1].name != sc.name:
                    players_list[sc.name] = [sc.wins, sc.spread, correction]
            except IndexError:
                players_list[sc.name] = [sc.wins, sc.spread, correction]

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


def format_pairings(pairs):
    cards_by_name = dict([(x.name, x) for x in cards])

    def fmtp(name):
        p = cards_by_name[name]
        return "**%s** (%d) (%.1lf-%.1lf %+d)" % (p.player.isc.lower(), p.player.rating, p.wins, p.losses, p.spread)

    def scoreOf(name):
        p = cards_by_name[name]
        return p.wins, p.spread, p.player.rating

    def scoreOf2(pair):
        [p1, p2] = pair
        m1 = sorted([scoreOf(p1), scoreOf(p2)], reverse=True)
        return m1

    ps = list(pairs)

    # Sort list so highest scoring players are on top.
    ps.sort(reverse=True, key=scoreOf2)
    # Sort each pair so best player is listed first.
    ps = [list(sorted(pair, reverse=True, key=scoreOf)) for pair in ps]

    lines = [" %s vs. %s" % (fmtp(p1), fmtp(p2)) for (p1, p2) in ps]

    # If there is a bye, show it.
    if len(byes) >= round_number:
        if byes[round_number - 1] and bye_group:
            lines.append(" **%s** BYE" % byes[round_number - 1].name)

    msg = "\n".join(lines)
    return msg


def pairings_swiss():
    # This is hardcoded to assume swiss pairings will only be used for the first round.
    # it simply chops the list in two [A1..An] and [B1..Bn], by rating where 
    # the A's are the top half and the B's are the bottom half.
    # It then pairs A1 vs B1, A2 vs B2, ..., An vs Bn.

    attendees = [p for p in players if p.attend]

    # Find all players but the bye, if there is  one.
    if byes:
        attendees = [x for x in attendees if x != byes[0]]

    # Sort players by their ratings.
    attendees.sort(reverse=True, key=lambda x: x.rating)

    # Since we have taken out the byes, the list should be even now.

    assert len(attendees) % 2 == 0

    n = len(attendees) // 2

    part1 = attendees[:n]  # Top half
    part2 = attendees[n:]  # Bottom half

    pairs = []
    for (p1, p2) in zip(part1, part2):
        pairs.append((p1.name, p2.name))

    return pairs
