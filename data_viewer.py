import pyfiglet
from prettytable import PrettyTable as pt

from database_managment import *
from parse_json_file import *


def view_tracked_players():
    players = get_tracked_players()

    t = pt()
    t.field_names = ['Tracked Players']

    for player in players:
        t.add_row([format_name(player['player_name'])])

    clear()
    print(t)
    print(f'Number of tracked players: {len(players)}')

    return 0


def view_clan_members():
    config = get_config('config.ini')

    clan_name = config['INFO']['clan_name']
    players = get_active_players()

    clear()
    banner = pyfiglet.figlet_format('Clan Members')
    print(banner)
    print(f'Clan: {clan_name}')
    print(f'Number of Members: {len(players)}')
    print(f'Last Updated: {players[0]["last_updated"]}\n')

    t = pt()
    t.field_names = ['Player Name', 'Role', 'Donations', 'Donations Received', 'Tracked']
    t.align['Player Name'] = 'l'

    for player in players:
        if player['role'] == 'leader':
            t.add_row([format_name(player['player_name']), format_role(player['role']), player['donations'], player['donations_received'], player['track']])

    co_leaders = [player for player in players if player['role'] == 'coLeader']
    admins = [player for player in players if player['role'] == 'admin']
    members = [player for player in players if player['role'] == 'member']

    for player in sorted(co_leaders, key=lambda i: (i['player_name'])):
        t.add_row([format_name(player['player_name']), format_role(player['role']), player['donations'], player['donations_received'], player['track']])

    for player in sorted(admins, key=lambda i: (i['player_name'])):
        t.add_row([format_name(player['player_name']), format_role(player['role']), player['donations'], player['donations_received'], player['track']])

    for player in sorted(members, key=lambda i: (i['player_name'])):
        t.add_row([format_name(player['player_name']), format_role(player['role']), player['donations'], player['donations_received'], player['track']])

    print(t)

    return 0


def view_war_stats():
    wars = get_war_ids()

    while True:
        print('Which war would you like to see?')
        for war in wars:
            print(f'{war["selector"]}) Start Time - {war["start_time"]}\n'
                  f'   Opponent - {war["enemy_clan_name"]}')
        try:
            user_ans = int(input('--> '))
            if user_ans in [war['selector'] for war in wars]:
                break
            else:
                print('Not a valid answer')
        except ValueError:
            print('Not a valid answer')

    for war in wars:
        if war['selector'] == user_ans:
            war_id = war['war_id']

    attack_data = get_clan_members_attacks(war_id)
    war_details = get_war_details(war_id)

    if war_details['clan_stars'] > war_details['opp_stars']:
        result = 'Win'
    elif war_details['clan_stars'] < war_details['opp_stars']:
        result = 'Lost'
    elif war_details['clan_stars'] == war_details['opp_stars']:
        if war_details['clan_destruction'] > war_details['opp_destruction']:
            result = 'Win'
        elif war_details['clan_destruction'] < war_details['opp_destruction']:
            result = 'Lost'
        elif war_details['clan_destruction'] == war_details['opp_destruction']:
            result = 'Tie'

    clear()
    banner = pyfiglet.figlet_format('Clan War Stats')
    print(banner)
    print(f'Result: {result}')
    print(f'Team Size: {war_details["team_size"]}')
    print(f'Start Time: {war_details["start_time"]}')
    print(f'End Time: {war_details["end_time"]}')
    print(f'Clan: {war_details["clan_name"]}')
    print(f'\tClan Level: \t\t{war_details["clan_level"]}')
    print(f'\tClan Attacks: \t\t{war_details["clan_attacks"]}')
    print(f'\tClan Stars: \t\t{war_details["clan_stars"]}')
    print(f'\tClan Destruction: \t{war_details["clan_destruction"]}%')
    print(f'Opponent: {war_details["opp_name"]}')
    print(f'\tOpponent Level: \t{war_details["opp_level"]}')
    print(f'\tOpponent Attacks: \t{war_details["opp_attacks"]}')
    print(f'\tOpponent Stars: \t{war_details["opp_stars"]}')
    print(f'\tOpponent Destruction: \t{war_details["opp_destruction"]}%')

    t = pt()
    t.field_names = ['Player Name', 'Map Position', 'Town Hall Level', 'Attacks Used', 'Stars', 'Total Destruction']
    t.align['Player Name'] = 'l'

    for player in attack_data:
        t.add_row([format_name(player['player_name']), player['map_position'], player['townhall_level'], player['attacks'], player['stars'],
                   player['total_destruction']])

    t.sortby = 'Map Position'
    print(t)

    return 0


def view_players_war_data():
    clear()
    banner = pyfiglet.figlet_format('Player War Stats')
    print(banner)

    t = pt()
    t.field_names = ['Rank', 'Player Name', 'Wars', 'Attacks', 'Stars', 'Total Destruction', 'Average Destruction']
    t.align['Player Name'] = 'l'

    active_players = get_active_players()
    war_players = []
    rank = 1

    for player in active_players:

        player_war_data = get_player_war_data(player['player_tag'])
        if player_war_data == 0:
            pass
        else:
            player_war_data['player_name'] = player['player_name']
            war_players.append(player_war_data)

    sorted_missed_attacks = sorted(war_players, key=lambda i: (i['missed_attacks']))

    missed_attacks = 0
    temp_list = []
    zero_attacks = []
    flush_list = False
    for count, player in enumerate(sorted_missed_attacks, 1):
        if player['missed_attacks'] == missed_attacks:
            if player['attacks'] == 0:
                zero_attacks.append(player)
            else:
                temp_list.append(player)
            # Triggers on the last record
            if count == len(sorted_missed_attacks):
                flush_list = True
        else:
            flush_list = True
            missed_attacks += 1

        if flush_list:
            flush_list = False
            for p in sorted(temp_list, key=lambda i: (i['missed_stars'])):
                t.add_row([rank, format_name(p['player_name']), p['wars'], p['attacks'], p['stars'], p['destruction'],
                           p['avg_destruction']])
                rank += 1
            temp_list = [player]

    for p in sorted(zero_attacks, key=lambda i: (i['player_name'])):
        t.add_row([rank, format_name(p['player_name']), p['wars'], p['attacks'], p['stars'], p['destruction'],
                   p['avg_destruction']])
        rank += 1

    # t.sortby = 'Attacks'
    # t.reversesort = True
    print(t)

    return 0


def view_recorded_clan_wars():
    print(get_clan_wars())


def view_league_war():
    config = get_config('config.ini')

    clan_tag = config['INFO']['clan_tag']
    seasons = get_league_seasons()

    clear()
    print('Select a season.')
    season = get_answer(seasons)

    rounds = get_league_war_rounds(season, clan_tag)

    t = pt()
    t.field_names = ['War Round', 'Start Time', 'End Time', 'Clan', 'Stars', 'Attacks', 'Destruction',
                     'Enemy Clan', 'Enemy Stars', 'Enemy Attacks', 'Enemy Destruction', 'Result']

    stats = {
        'wins': 0,
        'losses': 0,
        'draws': 0,
        'total_stars': 0,
        'total_attacks': 0,
        'total_destruction': 0.0,
        'team_size': int(rounds[0]['team_size'])
    }

    for war_round in rounds:
        if war_round['clan_stars'] > war_round['opp_stars']:
            result = 'Win'
            stats['wins'] += 1
        elif war_round['clan_stars'] < war_round['opp_stars']:
            result = 'Lost'
            stats['losses'] += 1
        elif war_round['clan_stars'] == war_round['opp_stars']:
            if war_round['clan_destruction'] > war_round['opp_destruction']:
                result = 'Win'
                stats['wins'] += 1
            elif war_round['clan_destruction'] < war_round['opp_destruction']:
                result = 'Lost'
                stats['losses'] += 1
            else:
                result = 'Draw'
                stats['draws'] += 1

        stats['total_stars'] += war_round['clan_stars']
        stats['total_attacks'] += war_round['clan_attacks']
        stats['total_destruction'] += war_round['clan_destruction']

        t.add_row([war_round['war_round'], format_timestamp(war_round['start_time']),
                   format_timestamp(war_round['end_time']), war_round['clan_name'], war_round['clan_stars'],
                   war_round['clan_attacks'], war_round['clan_destruction'], war_round['opp_name'],
                   war_round['opp_stars'], war_round['opp_attacks'], war_round['opp_destruction'], result])

    clear()
    banner = pyfiglet.figlet_format('League War')
    print(banner)
    print(f'League Season: {season}')
    print(f'Start Time: {format_timestamp(rounds[0]["start_time"])}')
    print(f'End Time: {format_timestamp(rounds[-1]["end_time"])}')
    print(f'Clan Name: {war_round["clan_name"]}')
    print(f'    Wins: {stats["wins"]}')
    print(f'    Losses: {stats["losses"]}')
    print(f'    Draws: {stats["draws"]}')
    print(f'    Clan Stars: {stats["total_stars"]}/{stats["team_size"] * 21}')
    print(f'    Clan Attacks: {stats["total_attacks"]}/{stats["team_size"] * 7}')
    print(f'    Clan Destruction: {format(stats["total_destruction"] / 700 * 100, ".2f")}%')
    print(t)

    print('\nEnter a round number to view more details, 8 to view overall or 9 to go back.')
    while True:
        try:
            user_ans = int(input('--> '))
            if 0 < user_ans < 10:
                break
        except ValueError:
            pass

    if user_ans < 8:
        for war_round in rounds:
            if war_round['war_round'] == user_ans:
                members = get_league_war_battles(war_round['war_id'])
                break

        t = pt()
        t.field_names = ['Player Name', 'Townhall Level', 'Map Position', 'Attacks', 'Stars', 'Destruction',
                         'Attack Order', 'Opponent Map Position']
        t.align['Player Name'] = 'l'

        for member in members:
            if member['clan_tag'] == clan_tag:
                t.add_row([format_name(member['player_name']), member['townhall_level'], member['map_position'],
                           member['attacks'],
                           member['stars'], member['destruction'], member['attack_order'], member['opp_map_position']])

        clear()
        print(banner)
        print(f'War Round: {war_round["war_round"]}')
        print(f'Start Time: {war_round["start_time"]}')
        print(f'End Time: {war_round["end_time"]}')
        print(f'Clan Name: {war_round["clan_name"]}')
        print(f'    Clan Attacks: {war_round["clan_attacks"]}')
        print(f'    Clan Stars: {war_round["clan_stars"]}')
        print(f'    Clan Destruction: {war_round["clan_destruction"]}')
        print(f'Opponent: {war_round["opp_name"]}')
        print(f'    Clan Attacks: {war_round["opp_attacks"]}')
        print(f'    Clan Stars: {war_round["opp_stars"]}')
        print(f'    Clan Destruction: {war_round["opp_destruction"]}')
        print(t)

    elif user_ans == 8:

        players = list()

        for war_round in rounds:
            members = get_league_war_battles(war_round['war_id'])
            for member in members:
                if member['clan_tag'] == clan_tag:
                    found = False
                    for player in players:
                        if member['player_tag'] == player['player_tag']:
                            player['attacks'] += member['attacks']
                            player['stars'] += member['stars']
                            player['destruction'] += member['destruction']
                            found = True
                            break
                    if not found:
                        players.append(member)

        t = pt()
        t.field_names = ['Player Name', 'Townhall Level', 'Attacks', 'Stars', 'Destruction']

        for player in players:
            t.add_row([format_name(player['player_name']), player['townhall_level'], f'{player["attacks"]}/7',
                       f'{player["stars"]}/21', f'{format(player["destruction"] / 700 * 100, ".1f")}%'])

        clear()
        banner = pyfiglet.figlet_format('Overall Stats')
        print(banner)
        print(f'League War Season: {season}')
        print(f'Clan Name: {war_round["clan_name"]}')
        print(t)

        # TODO Add a top and bottom performers view
