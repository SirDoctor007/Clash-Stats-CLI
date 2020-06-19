import logging

from database_managment import get_next_war_id
from main_functions import *

logger = logging.getLogger(__name__)


def parse_player_file(file_path):
    try:
        with open(file_path, 'r') as file_data:
            data = json.load(file_data)
    except FileNotFoundError as error:
        logger.error(error)
        return -1

    file_path = str(file_path)[str(file_path).find('Player') + 7:]
    split = file_path.split('_')

    player_data = {'id': f'{data["timestamp"]}_{data["tag"]}',
                   'timestamp': data['timestamp'],
                   'player_tag': data['tag'],
                   'player_name': data['name'],
                   'townhall_level': data['townHallLevel'],
                   'exp_level': data['expLevel'],
                   'league': data['league']['name'],
                   'trophies': data['trophies'],
                   'best_trophies': data['bestTrophies'],
                   'war_stars': data['warStars'],
                   'attack_wins': data['attackWins'],
                   'defense_wins': data['defenseWins'],
                   'builderhall_level': data['builderHallLevel'],
                   'versus_trophies': data['versusTrophies'],
                   'best_versus_trophies': data['bestVersusTrophies'],
                   'versus_battle_wins': data['versusBattleWins'],
                   'clan_tag': data['clan']['tag'],
                   'clan_name': data['clan']['name'],
                   'clan_level': data['clan']['clanLevel'],
                   'role': data['role'],
                   'donations': data['donations'],
                   'donations_received': data['donationsReceived'],
                   'looted_gold': data['achievements'][5]['value'],
                   'looted_elixer': data['achievements'][6]['value'],
                   'looted_dark_elixer': data['achievements'][16]['value']}

    return player_data


def parse_clan_members(file_path):
    try:
        with open(file_path, 'r') as file_data:
            data = json.load(file_data)
    except FileNotFoundError:
        logger.error(exc_info=True)
        return -1

    members = []

    for player in data['items']:
        player_data = {'player_tag': player['tag'],
                       'player_name': player['name'],
                       'role': player['role'],
                       'donations': player['donations'],
                       'donations_received': player['donationsReceived'],
                       'track': 'N',
                       'last_updated': data['timestamp']}
        members.append(player_data)

    return members


def parse_clan_war_file(file_path):
    war_id = get_next_war_id()

    try:
        with open(file_path, 'r') as file_data:
            data = json.load(file_data)
    except FileNotFoundError:
        logger.error(exc_info=True)
        return -1

    try:
        if data['state'] != 'warEnded':
            print('File must be a "War Ended" file')
            return -1
    except KeyError:
        print('Not a valid file')
        return -1

    clan_war_details = {
        'war_id': war_id,
        'team_size': data['teamSize'],
        'start_time': convert_timestamp(data['startTime']),
        'end_time': convert_timestamp(data['endTime']),
        'home_clan_tag': data['clan']['tag'],
        'home_clan_name': data['clan']['name'],
        'home_clan_level': data['clan']['clanLevel'],
        'home_clan_attacks': data['clan']['attacks'],
        'home_clan_stars': data['clan']['stars'],
        'home_clan_destruction': data['clan']['destructionPercentage'],
        'enemy_clan_tag': data['opponent']['tag'],
        'enemy_clan_name': data['opponent']['name'],
        'enemy_clan_level': data['opponent']['clanLevel'],
        'enemy_clan_attacks': data['opponent']['attacks'],
        'enemy_clan_stars': data['opponent']['stars'],
        'enemy_clan_destruction': data['opponent']['destructionPercentage'],
    }

    clan_war_members = []
    for player in data['clan']['members']:
        try:
            attacks = len(player['attacks'])
            stars = 0
            destruction = 0
            for attack in player['attacks']:
                stars += attack['stars']
                destruction += attack['destructionPercentage']
        except KeyError:
            attacks = 0
            stars = 0
            destruction = 0

        member = {
            'war_id': war_id,
            'clan_tag': data['clan']['tag'],
            'player_tag': player['tag'],
            'player_name': player['name'],
            'townhall_level': player['townhallLevel'],
            'map_position': player['mapPosition'],
            'attacks': attacks,
            'defends': player['opponentAttacks'],
            'stars': stars,
            'destruction': destruction
        }
        clan_war_members.append(member)

    for player in data['opponent']['members']:
        try:
            attacks = len(player['attacks'])
            stars = 0
            destruction = 0
            for attack in player['attacks']:
                stars += attack['stars']
                destruction += attack['destructionPercentage']
        except KeyError:
            attacks = 0
            stars = 0
            destruction = 0

        member = {
            'war_id': war_id,
            'player_tag': player['tag'],
            'player_name': player['name'],
            'clan_tag': data['opponent']['tag'],
            'townhall_level': player['townhallLevel'],
            'map_position': player['mapPosition'],
            'attacks': attacks,
            'defends': player['opponentAttacks'],
            'stars': stars,
            'destruction': destruction
        }
        clan_war_members.append(member)

    attacks = []
    for player in data['clan']['members']:
        try:
            for attack in player['attacks']:
                attack['war_id'] = war_id
                attack['type'] = 'attack'
                attacks.append(attack)
        except KeyError:
            pass

    for player in data['opponent']['members']:
        try:
            for attack in player['attacks']:
                attack['war_id'] = war_id
                attack['type'] = 'defend'
                attacks.append(attack)
        except KeyError:
            pass

    return clan_war_details, clan_war_members, attacks


def parse_league_war_file(file_path):
    try:
        with open(file_path, 'r') as file_data:
            data = json.load(file_data)
    except FileNotFoundError:
        logger.error(exc_info=True)
        return -1

    league_clans = []
    for clan in data['clans']:
        clan_data = {
            'id': f'{data["season"]}_{clan["tag"]}',
            'league_season': data['season'],
            'clan_tag': clan['tag'],
            'clan_name': clan['name'],
            'clan_level': clan['clanLevel'],
            'num_members': len(clan['members'])
        }
        league_clans.append(clan_data)

    league_wars = []
    for round_num, war_round in enumerate(data['rounds'], 1):
        for war_tag in war_round['warTags']:
            if war_tag != '#0':
                war_data = {
                    'war_id': f'{data["season"]}_{round_num}_{war_tag}',
                    'league_season': data['season'],
                    'war_round': round_num,
                    'war_tag': war_tag
                }
                league_wars.append(war_data)

    return league_clans, league_wars


def parse_war_file(file_path, war_data):
    try:
        with open(file_path, 'r') as file_data:
            data = json.load(file_data)
    except FileNotFoundError:
        logger.error(exc_info=True)
        return -1

    war_data2 = {
        'team_size': data['teamSize'],
        'start_time': convert_timestamp(data['startTime']),
        'end_time': convert_timestamp(data['endTime']),
        'clan1_tag': data['clan']['tag'],
        'clan1_attacks': data['clan']['attacks'],
        'clan1_stars': data['clan']['stars'],
        'clan1_destruction': format(data['clan']['destructionPercentage'], '.1f'),
        'clan2_tag': data['opponent']['tag'],
        'clan2_attacks': data['opponent']['attacks'],
        'clan2_stars': data['opponent']['stars'],
        'clan2_destruction': format(data['opponent']['destructionPercentage'], '.1f')
    }
    war_data.update(war_data2)

    league_players = []
    league_battles = []

    parameters = ['clan', 'opponent']
    for parameter in parameters:
        for player in data[parameter]['members']:
            player_data = {
                'id': f'{war_data["war_id"]}_{player["tag"]}',
                'war_id': war_data['war_id'],
                'player_tag': player['tag'],
                'player_name': player['name'],
                'townhall_level': player['townhallLevel'],
                'map_position': player['mapPosition'],
                'clan_tag': data[parameter]['tag'],
                'defends': player['opponentAttacks']
            }
            try:
                player_data['attacks'] = len(player['attacks'])
            except KeyError:
                player_data['attacks'] = 0
            league_players.append(player_data)

            try:
                for attack in player['attacks']:
                    player_attack_data = {
                        'id': f'{war_data["war_id"]}_{attack["attackerTag"]}',
                        'war_id': war_data['war_id'],
                        'attacker_tag': attack['attackerTag'],
                        'defender_tag': attack['defenderTag'],
                        'stars': attack['stars'],
                        'destruction': attack['destructionPercentage'],
                        'attack_order': attack['order']
                    }
                    league_battles.append(player_attack_data)
            except KeyError:
                pass

    return war_data, league_players, league_battles
