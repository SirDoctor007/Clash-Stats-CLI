from prettytable import PrettyTable as pt
import pyfiglet
import configparser
from database_managment import get_tracked_players, get_active_players, get_war_ids, get_clan_members_attacks, get_war_details, get_player_war_data, get_clan_wars
from main_functions import *
from parse_json_file import *


def view_tracked_players():
    players = get_tracked_players()

    t = pt()
    t.field_names = ['Tracked Players']

    for player in players:
        t.add_row([format_name(player['player_name'])])

    print(t)
    print(f'Number of tracked players: {len(players)}')

    return 0


def view_clan_members():
    config = configparser.ConfigParser()
    config.read('config.ini')

    clan_name = config['DEFAULT']['clan_name']
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
    config = configparser.ConfigParser()
    config.read('config.ini')

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


def view_league_war_round():
    config = configparser.ConfigParser()
    config.read('config.ini')

    clear()
    banner = pyfiglet.figlet_format('League Round')
    print(banner)
    print('Select a Season\n')
    file = find_file_options(Path(config['DEFAULT']['data_folder'], 'League War'), False, 1)
    clans, _ = parse_league_war_file(file)
    clan_list = list()
    # clans_list = [{'key': enu, 'clan_name': clan['clan_name'], 'clan_id': clan['id']} for enu, clan in enumerate(clans, 1)]
    # print(clans_list)

    while True:
        clear()
        print(banner)
        print('Select a Clan')
        for enu, clan in enumerate(clans, 1):
            print(f'{enu}) {clan["clan_name"]}')
            clan_list.append((enu, clan['id']))
        try:
            user_ans = int(input('--> '))
            if user_ans in range(1, enu + 1):
                break
            else:
                raise ValueError
        except ValueError:
            print('Not a Valid Answer')
            _ = input('Press Enter to Try Again...')

    for option in clan_list:
        if option[0] == user_ans:
            for clan in clans:
                if clan['id'] == option[1]:
                    break



