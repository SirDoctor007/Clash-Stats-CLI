import logging.handlers
import sqlite3

from main_functions import *

logger = logging.getLogger(__name__)


'''
PRIMARY FUNCTIONS
'''


def connect():
    config = configparser.ConfigParser()
    config.read(Path('Config', 'database.ini'))

    database = Path(config['INFO']['database_name'])

    conn = sqlite3.connect(database)
    logger.debug(f'Connected to {database}')
    return conn


def create_database():
    config = configparser.ConfigParser()
    config.read(Path('Config', 'database.ini'))

    database = Path(config['INFO']['database_name'])

    if Path.is_file(database):
        question = [
            {
                'type': 'confirm',
                'name': 'confirm',
                'message': 'The database already exists. Do you want to overwrite it?',
                'default': False
            }
        ]
        answer = prompt(question)
        if not answer['confirm']:
            print('\nAborting database creation...')
            return -1
        else:
            try:
                Path.unlink(database)
            except PermissionError:
                print('')
                print('Unable to recreate the database as it is open in another process')
                print('Aborting database creation...')
                return -1
    print('Creating Database...')
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Players Table
    c.execute('''DROP TABLE IF EXISTS players''')
    c.execute(config['TABLES']['players'])
    logger.info('Created table "players"')

    # Player Info Table
    c.execute('''DROP TABLE IF EXISTS player_record''')
    c.execute(config['TABLES']['player_record'])
    logger.info('Created table "player_record"')

    # Clan War Table
    c.execute('''DROP TABLE IF EXISTS clan_war''')
    c.execute(config['TABLES']['clan_war'])
    logger.info('Created table "clan_war"')

    # Clan War Members Table
    c.execute('''DROP TABLE IF EXISTS clan_war_members''')
    c.execute(config['TABLES']['clan_war_members'])
    logger.info('Created table "clan_war_members"')

    # Clan War Battles Table
    c.execute('''DROP TABLE IF EXISTS clan_war_battles''')
    c.execute(config['TABLES']['clan_war_battles'])
    logger.info('Created table "clan_war_battles"')

    # Clan War League War Table
    c.execute('''DROP TABLE IF EXISTS league_wars''')
    c.execute(config['TABLES']['league_wars'])
    logger.info('Created table "league_wars"')

    # Clan League War Clan Info Table
    c.execute('''DROP TABLE IF EXISTS league_clans''')
    c.execute(config['TABLES']['league_clans'])
    logger.info('Created table "league_clans"')

    # Clan League War Battles Table
    c.execute('''DROP TABLE IF EXISTS league_battles''')
    c.execute(config['TABLES']['league_battles'])
    logger.info('Created table "league_battles"')

    # Clan League War Battle Members Table
    c.execute('''DROP TABLE IF EXISTS league_players''')
    c.execute(config['TABLES']['league_players'])
    logger.info('Created table "league_players"')

    conn.commit()
    conn.close()

    return 0


''''
####################################################################
************************ CLAN WAR FUNCTIONS ************************
####################################################################
'''


# Returns 0 if successful
def insert_clan_war(clan_war_obj, verbose=False):
    details = clan_war_obj.details
    members = clan_war_obj.members
    attacks = clan_war_obj.attacks

    if get_recorded_status(str(details['start_time'])):
        if verbose:
            print(f'{format_name(details["home_clan_name"])} vs {format_name(details["enemy_clan_name"])} has '
                        f'already been recorded. Aborting...')
        return -1

    conn = connect()
    c = conn.cursor()

    # Inserts the details of the clan war
    try:
        c.execute('''INSERT INTO clan_war VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (details['war_id'],
                   details['team_size'],
                   details['start_time'],
                   details['end_time'],
                   details['home_clan_tag'],
                   details['home_clan_name'],
                   details['home_clan_level'],
                   details['home_clan_attacks'],
                   details['home_clan_stars'],
                   details['home_clan_destruction'],
                   details['enemy_clan_tag'],
                   details['enemy_clan_name'],
                   details['enemy_clan_level'],
                   details['enemy_clan_attacks'],
                   details['enemy_clan_stars'],
                   details['enemy_clan_destruction'])
                  )
        if verbose:
            print(f'{format_name(details["home_clan_name"])} vs {format_name(details["enemy_clan_name"])} details '
                  f'has been inserted into clan_war')
    except sqlite3.IntegrityError:
        logger.error(f'The "war_id" of {details["war_id"]} has already been used.')
        if verbose:
            print('There was an error with the generated war_id.')
        conn.close()
        return -1

    # Inserts the members of the clan war to the database
    for player in members:
        c.execute('''INSERT INTO clan_war_members VALUES (?,?,?,?,?,?,?,?,?,?)''',
                  (player['war_id'],
                   player['clan_tag'],
                   player['player_tag'],
                   player['player_name'],
                   player['townhall_level'],
                   player['map_position'],
                   player['attacks'],
                   player['defends'], player['stars'],
                   player['destruction']))

    if verbose:
        print(f'{format_name(details["home_clan_name"])} vs {format_name(details["enemy_clan_name"])} members have '
                    f'been inserted into clan_war_members')

    # Inserts the attack details for each member
    for attack in attacks:
        c.execute('''INSERT INTO clan_war_battles VALUES (?,?,?,?,?,?,?)''',
                  (attack['war_id'],
                   attack['type'],
                   attack['attackerTag'],
                   attack['defenderTag'],
                   attack['stars'],
                   attack['destructionPercentage'],
                   attack['order']))

    if verbose:
        print(f'{format_name(details["home_clan_name"])} vs {format_name(details["enemy_clan_name"])} attacks have '
                    f'been inserted into clan_war_battles')

        print(f'\nCompleted inserting {clan_war_obj.file_path}!')

    conn.commit()
    conn.close()

    return 0


def get_war_details(war_id):
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT team_size, start_time, end_time, home_clan_name, home_clan_level, home_clan_attacks, home_clan_stars,
                        home_clan_destruction, enemy_clan_name, enemy_clan_level, enemy_clan_attacks, enemy_clan_stars, 
                        enemy_clan_destruction
                   FROM clan_war 
                  WHERE war_id = ?''', (str(war_id),))
    r = c.fetchone()
    conn.close()

    details = {
        'team_size': r[0],
        'start_time': r[1],
        'end_time': r[2],
        'clan_name': r[3],
        'clan_level': r[4],
        'clan_attacks': r[5],
        'clan_stars': r[6],
        'clan_destruction': r[7],
        'opp_name': r[8],
        'opp_level': r[9],
        'opp_attacks': r[10],
        'opp_stars': r[11],
        'opp_destruction': r[12]
    }

    return details


def get_clan_members_attacks(war_id):
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT player_name, townhall_level, map_position, attacks, stars, total_destruction
                   FROM clan_war_members 
                  WHERE clan_tag = "#2YC9YR9J" 
                    AND war_id = ?''', (str(war_id),))
    r = c.fetchall()
    conn.close()

    participants = []

    for member in r:
        member_data = {
            'player_name': member[0],
            'townhall_level': member[1],
            'map_position': member[2],
            'attacks': member[3],
            'stars': member[4],
            'total_destruction': member[5]
        }
        participants.append(member_data)

    return participants


def get_player_war_data(player_tag):
    conn = connect()
    c = conn.cursor()
    c.execute('''SELECT player_tag, player_name, attacks, stars, total_destruction
                   FROM clan_war_members
                   WHERE player_tag = ?''', (player_tag,))
    r = c.fetchall()
    conn.close()

    attacks = 0
    stars = 0
    destruction = 0

    for count, item in enumerate(r, 1):
        attacks += item[2]
        stars += item[3]
        destruction += item[4]

    try:
        player_data = {
            'player_tag': player_tag,
            'wars': count,
            'attacks': f'{attacks}/{count * 2}',
            'stars': f'{stars}/{count * 6}',
            'destruction': f'{destruction}/{count * 200}',
            'avg_destruction': f'{format(destruction / attacks, ".1f")}%',
            'missed_attacks': count * 2 - attacks,
            'missed_stars': count * 6 - stars
        }
    except ZeroDivisionError:
        player_data = {
            'player_tag': player_tag,
            'wars': count,
            'attacks': 0,
            'stars': 0,
            'destruction': 0,
            'avg_destruction': 0,
            'missed_attacks': 500,
            'missed_stars': 500
        }
    except:
        return 0

    return player_data


# Determines if the clan war has already been recorded
def get_recorded_status(start_time):
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT start_time FROM clan_war''')
    r = c.fetchall()

    conn.close()

    start_times = []
    for item in r:
        start_times.append(item[0])

    if start_time in start_times:
        return True
    else:
        return False


def get_next_war_id():
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT MAX(war_id) FROM clan_war''')
    r = c.fetchone()

    conn.close()

    if r[0]:
        return r[0] + 1
    else:
        return 100


def get_war_ids():
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT war_id, start_time, enemy_clan_name FROM clan_war''')
    r = c.fetchall()

    conn.close()

    war_info = []
    for count, item in enumerate(r):
        war_data = {'selector': count + 1, 'war_id': item[0], 'start_time': item[1], 'enemy_clan_name': item[2]}
        war_info.append(war_data)

    return war_info


def remove_clan_war():
    wars = get_clan_wars()

    clan_name = get_answer([war['enemy_clan_name'] for war in wars])
    for war in wars:
        if clan_name == war['enemy_clan_name']:
            war_id = war['war_id']

    conn = connect()
    c = conn.cursor()

    c.execute('''DELETE FROM clan_war WHERE war_id = ?''', (war_id,))
    c.execute('''DELETE FROM clan_war_battles WHERE war_id = ?''', (war_id,))
    c.execute('''DELETE FROM clan_war_members WHERE war_id = ?''', (war_id,))

    conn.commit()
    conn.close()


def get_clan_wars():
    conn = connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''SELECT war_id, team_size, start_time, home_clan_name, enemy_clan_name FROM clan_war''')

    r = c.fetchall()
    conn.close()

    wars = [dict(row) for row in r]

    return wars


'''
####################################################################
************************* PLAYER FUNCTIONS *************************
####################################################################
'''


def insert_players_from_clan(members, verbose=False):
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT player_tag, player_name FROM players''')
    r = c.fetchall()
    old_members = [{'player_tag': t[0], 'player_name': t[1]} for t in r]
    active_members = [player['player_tag'] for player in members]
    updated_players = list()

    if verbose:
        print('\n----Removed Players----')
    for player in old_members:
        if player['player_tag'] not in active_members:
            c.execute(f'''DELETE FROM players
                           WHERE player_tag = "{player['player_tag']}"''')
            if verbose:
                print(f'Removed {format_name(player["player_name"])}')

    if verbose:
        print('\n----Added Players----')
    for player in members:
        try:
            c.execute('''INSERT INTO players VALUES (?,?,?,?,?, ?, ?)''', (player['player_tag'],
                                                                           player['player_name'],
                                                                           player['role'],
                                                                           player['donations'],
                                                                           player['donations_received'],
                                                                           player['track'],
                                                                           player['last_updated']))
            if verbose:
                print(f'Inserted {format_name(player["player_name"])}')
        except sqlite3.OperationalError:
            logger.error(exc_info=True)
            if verbose:
                print('There was an error inserting a clan member. See the error log for more info.')
        except sqlite3.IntegrityError:
            c.execute(f'''UPDATE players 
                             SET role = "{player['role']}",
                                 donations = "{player['donations']}",
                                 donations_received = "{player['donations_received']}",
                                 last_updated = "{player['last_updated']}"
                           WHERE player_tag = "{player['player_tag']}"''')
            updated_players.append(format_name(player["player_name"]))

    if verbose:
        print('\n----Updated Players----')
        for updated_player in updated_players:
            print(f'Updated {updated_player}')

    conn.commit()
    conn.close()


# TODO Change this function to allow inserting multiple players at a time
def insert_player_record_data(player_data, verbose=False):
    conn = connect()
    c = conn.cursor()
    insert_string = 'INSERT INTO player_record VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    try:
        c.execute(insert_string, (player_data['id'],
                                  player_data['timestamp'],
                                  player_data['player_tag'],
                                  player_data['player_name'],
                                  player_data['townhall_level'],
                                  player_data['exp_level'],
                                  player_data['league'],
                                  player_data['trophies'],
                                  player_data['best_trophies'],
                                  player_data['war_stars'],
                                  player_data['attack_wins'],
                                  player_data['defense_wins'],
                                  player_data['builderhall_level'],
                                  player_data['versus_trophies'],
                                  player_data['best_versus_trophies'],
                                  player_data['versus_battle_wins'],
                                  player_data['clan_tag'],
                                  player_data['clan_name'],
                                  player_data['clan_level'],
                                  player_data['role'],
                                  player_data['donations'],
                                  player_data['donations_received'],
                                  player_data['looted_gold'],
                                  player_data['looted_elixer'],
                                  player_data['looted_dark_elixer']))
        if verbose:
            print(f'Inserted {format_name(player_data["player_name"])} {player_data["timestamp"]} to player_record')
    # Player record has already been recorded
    except sqlite3.IntegrityError:
        if verbose:
            print(f'Skipping {format_name(player_data["player_name"])} {player_data["timestamp"]}')
    except sqlite3.OperationalError:
        logger.error(exc_info=True)
        if verbose:
            print('There was an error inserting player data. See the error log for more info.')
    finally:
        conn.commit()
        conn.close()

    return 0


# Updates members to track
def update_tracked_players():
    players = get_active_players()
    tracked_players = []
    choices = []

    for player in players:
        if player['track'] == 'Y':
            track = True
            tracked_players.append(player)
        else:
            track = False
        choices.append({'name': player['player_name'],
                        'checked': track})

    questions = [
        {
            'type': 'checkbox',
            'message': 'Select Players to Track',
            'name': 'players',
            'choices': choices
        }
    ]

    answers = prompt(questions)

    conn = connect()
    c = conn.cursor()

    # Removes players who where not selected and are currently tracked
    tracked_list = []
    for player in tracked_players:
        if player['player_name'] not in answers['players']:
            # Update player in database, by removing tracked indicator
            c.execute(f'''UPDATE players 
                             SET track = "N"
                           WHERE player_tag = "{player['player_tag']}"''')
        else:
            tracked_list.append(player['player_name'])

    # Adds new players to track
    for player in answers['players']:
        if player not in tracked_list:
            for p in players:
                if p['player_name'] == player:
                    player_tag = p['player_tag']
                    break
            c.execute(f'''UPDATE players 
                             SET track = "Y"
                           WHERE player_tag = "{player_tag}"''')

    conn.commit()
    conn.close()

    clear()
    print(f'----Tracking {len(answers["players"])} players----')
    for player in answers['players']:
        print(player)

    return 0


def get_active_players():
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT * FROM players''')
    r = c.fetchall()

    conn.close()

    players = []
    for player in r:
        player_data = {'player_tag': player[0],
                       'player_name': player[1],
                       'role': player[2],
                       'donations': player[3],
                       'donations_received': player[4],
                       'track': player[5],
                       'last_updated': player[6]}
        players.append(player_data)

    return players


# Returns a list of players to be tracked
def get_tracked_players():
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT player_tag, player_name FROM players WHERE track = "Y"''')
    r = c.fetchall()

    conn.close()

    players = []
    for player in r:
        player_data = {'player_tag': player[0], 'player_name': player[1]}
        players.append(player_data)

    return players


'''
####################################################################
*********************** LEAGUE WAR FUNCTIONS ***********************
####################################################################
'''


def insert_league_war_data(league_war_obj, verbose=False):
    conn = connect()
    c = conn.cursor()

    for clan in league_war_obj.clans:
        try:
            c.execute('''INSERT INTO league_clans VALUES (?,?,?,?,?,?)''', (
                clan['id'],
                clan['league_season'],
                clan['clan_tag'],
                clan['clan_name'],
                clan['clan_level'],
                clan['num_members']
            ))
            if verbose:
                print(f'Inserted {format_name(clan["clan_name"])} into league_clans')
        # Clan has already been placed in the database
        except sqlite3.IntegrityError:
            if verbose:
                print(f'Skipped inserting {format_name(clan["clan_name"])} into league_clans')

    for player in league_war_obj.players:
        try:
            c.execute('''INSERT INTO league_players VALUES (?,?,?,?,?,?,?,?,?)''', (
                player['id'],
                player['war_id'],
                player['player_tag'],
                player['player_name'],
                player['townhall_level'],
                player['map_position'],
                player['clan_tag'],
                player['attacks'],
                player['defends']
            ))
            if verbose:
                print(f'Inserted {format_name(player["player_name"])} into league_players')
        # Player has already been placed in the database
        except sqlite3.IntegrityError:
            if verbose:
                print(f'Skipped inserting {format_name(player["player_name"])} into league_players')

    for war in league_war_obj.wars:
        try:
            c.execute('''INSERT INTO league_wars VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                war['war_id'],
                war['league_season'],
                war['war_round'],
                war['war_tag'],
                war['team_size'],
                war['start_time'],
                war['end_time'],
                war['clan1_tag'],
                war['clan1_attacks'],
                war['clan1_stars'],
                war['clan1_destruction'],
                war['clan2_tag'],
                war['clan2_attacks'],
                war['clan2_stars'],
                war['clan2_destruction']
            ))
            if verbose:
                print(f'Inserted {war["war_tag"]} into league_wars')
        # War has already been placed in the database
        except sqlite3.IntegrityError:
            if verbose:
                print(f'Skipped inserting {war["war_tag"]} into league_wars')

    for battle in league_war_obj.battles:
        try:
            c.execute('''INSERT INTO league_battles VALUES (?,?,?,?,?,?,?)''', (
                battle['id'],
                battle['war_id'],
                battle['attacker_tag'],
                battle['defender_tag'],
                battle['stars'],
                battle['destruction'],
                battle['attack_order']
            ))
            if verbose:
                print(f'Inserted {battle["id"]} into league_battles')
        # Battle has already been placed in the database
        except sqlite3.IntegrityError:
            if verbose:
                print(f'Skipped inserting {battle["id"]} into league_battles')

    conn.commit()
    conn.close()


def get_recorded_league_wars(league_war_id):
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT war_tag FROM league_war_battles WHERE league_war_id = ?''', (league_war_id,))
    r = c.fetchall()
    conn.close()

    if len(r) == 0:
        return r
    else:
        return [war_tag for t in r for war_tag in t]


# Returns a list of league war rounds for a specified season and clan.
def get_league_war_rounds(league_season, clan_tag):
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT lw.war_id, 
                        lw.war_round, 
                        lw.team_size, 
                        lw.start_time, 
                        lw.end_time, 
                        lw.clan1_tag, 
                        lca.clan_name,
                        lw.clan1_attacks,
                        lw.clan1_stars,
                        lw.clan1_destruction,
                        lw.clan2_tag, 
                        lcb.clan_name,
                        lw.clan2_attacks,
                        lw.clan2_stars,
                        lw.clan2_destruction
                   FROM league_wars lw, 
                        league_clans lca, 
                        league_clans lcb
                  WHERE lw.league_season = ?
                    AND lca.league_season = ?
                    AND lcb.league_season = ?
                    AND lca.clan_tag = lw.clan1_tag
                    AND lcb.clan_tag = lw.clan2_tag
                    AND (clan1_tag = ? 
                        OR clan2_tag = ?)''', (league_season, league_season, league_season, clan_tag, clan_tag))
    r = c.fetchall()

    rounds = list()

    for war_round in r:
        round_data = {
            'war_id': war_round[0],
            'war_round': war_round[1],
            'team_size': war_round[2],
            'start_time': war_round[3],
            'end_time': war_round[4],
            'clan_tag': clan_tag

        }
        if war_round[5] == clan_tag:
            round_data['clan_name'] = war_round[6]
            round_data['clan_attacks'] = war_round[7]
            round_data['clan_stars'] = war_round[8]
            round_data['clan_destruction'] = war_round[9]
            round_data['opp_tag'] = war_round[10]
            round_data['opp_name'] = war_round[11]
            round_data['opp_attacks'] = war_round[12]
            round_data['opp_stars'] = war_round[13]
            round_data['opp_destruction'] = war_round[14]
        else:
            round_data['clan_name'] = war_round[11]
            round_data['clan_attacks'] = war_round[12]
            round_data['clan_stars'] = war_round[13]
            round_data['clan_destruction'] = war_round[14]
            round_data['opp_tag'] = war_round[5]
            round_data['opp_name'] = war_round[6]
            round_data['opp_attacks'] = war_round[7]
            round_data['opp_stars'] = war_round[8]
            round_data['opp_destruction'] = war_round[9]

        rounds.append(round_data)

    return rounds


def get_league_war_battles(war_id):
    conn = connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''SELECT player_tag, player_name, townhall_level, map_position, clan_tag, attacks
                   FROM league_players
                  WHERE war_id = ?''', (war_id,))

    members = sorted([dict(row) for row in c.fetchall()], key=lambda i: (i['map_position']))

    c.execute('''SELECT attacker_tag, defender_tag, stars, destruction, attack_order
                   FROM league_battles
                   WHERE war_id = ?''', (war_id,))

    battles = [dict(row) for row in c.fetchall()]

    for member in members:
        found = False
        for battle in battles:
            if member['player_tag'] == battle['attacker_tag']:
                found = True
                member['stars'] = battle['stars']
                member['destruction'] = battle['destruction']
                member['attack_order'] = battle['attack_order']
                for opponent in members:
                    if opponent['player_tag'] == battle['defender_tag']:
                        member['opp_map_position'] = opponent['map_position']
        if not found:
            member['stars'] = 0
            member['destruction'] = 0
            member['attack_order'] = 'N/A'
            member['opp_map_position'] = 'N/A'

    return members


# Returns a list of recorded league war seasons
def get_league_seasons():
    conn = connect()
    c = conn.cursor()

    c.execute('''SELECT DISTINCT league_season FROM league_wars''')
    r = c.fetchall()

    conn.close()

    seasons = list()
    for t in r:
        seasons.append(t[0])

    return seasons

'''
Un-used Functions
'''

# def import_folder_player_record_data(folder):
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#
#     database = config['DEFAULT']['database']
#     json_files = []
#     player_tag = ''
#
#     for root, directories, files in os.walk(folder):
#         for file in files:
#             split = file.split('.')
#             if split[1] == 'json':
#                 json_files.append(file)
#
#     conn = sqlite3.connect(database)
#     c = conn.cursor()
#
#     for file in json_files:
#         file_path = folder / file
#         data = parse_player_file(file_path)
#
#         if player_tag != data['player_tag']:
#             timestamps = []
#             player_tag = data['player_tag']
#             c.execute('''SELECT timestamp FROM player_info WHERE player_tag = ?''', (player_tag,))
#
#             for item in c.fetchall():
#                 timestamps.append(item[0])
#
#         if data['timestamp'] in timestamps:
#             print(f'{file} has already been added to the database. Skipping.')
#         else:
#             print(f'Inserting {file} into the database.')
#             try:
#                 c.execute('''INSERT INTO player_info VALUES (?,?,?,?,?,?)''', (data['timestamp'],
#                                                                                data['player_tag'],
#                                                                                data['player_name'],
#                                                                                data['looted_gold'],
#                                                                                data['looted_elixer'],
#                                                                                data['looted_dark_elixer']))
#                 logger.info('Inserted row to table "player_info"')
#             except sqlite3.OperationalError as error:
#                 logger.error(error)
#
#     conn.commit()
#     conn.close()
