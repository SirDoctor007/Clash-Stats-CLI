import configparser
import requests
import base64
import logging
import json
import html
from pathlib import Path
from tqdm import tqdm
from ftplib import FTP
from database_managment import *
from parse_json_file import *


logger = logging.getLogger(__name__)


def get_player_data(submit_to_database):
    config = get_config('secrets.ini')
    headers = {'Accept': 'application/json', 'authorization': base64.b64decode(config['INFO']['api_token']).decode()}

    config = get_config('config.ini')

    player_tags = get_tracked_players()

    timestamp = get_timestamp()
    date, time = str(timestamp).split(' ')

    for player in player_tags:
        url = config['INFO']['player_url'] + requests.utils.quote(player['player_tag'])

        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            logger.warning(f'Get player data returned {r.status_code}')
        else:
            logger.info(f'Get player data returned {r.status_code}')

            content = r.json()
            content['timestamp'] = str(timestamp)

            file = f'{date}_{time[:5].replace(":", "-")}_{format_name(content["name"])}.json'
            file_path = Path(config['INFO']['data_folder'], 'Player', file)

            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2)

            if submit_to_database:
                insert_player_record_data(parse_player_file(file_path))

    return 0


def get_player_data_ftp(submit_to_database):
    config = get_config('secrets.ini')

    ftp = FTP(config['INFO']['ftp_ip'])
    ftp.login(config['INFO']['ftp_user'], config['INFO']['ftp_pass'])
    files = ftp.nlst('Player_Data')

    config = get_config('config.ini')

    if len(files) == 0:
        print('There are no player records to pull')
    else:
        print(f'\nRetrieving {len(files)} files...\n')
        for file in tqdm(files):
            split = file.split('/')
            file_path = Path(config['INFO']['data_folder'], 'Player', split[1])
            with open(file_path, 'wb') as f:
                ftp.retrbinary(f'RETR {file}', f.write)
            ftp.delete(file)

            if submit_to_database:
                insert_player_record_data(parse_player_file(file_path))
        print('\nCompleted!')
    ftp.quit()

    return 0


def get_clan_members(submit_to_database):
    config = get_config('secrets.ini')
    headers = {'Accept': 'application/json', 'authorization': base64.b64decode(config['INFO']['api_token']).decode()}

    config = get_config('config.ini')
    url = config['INFO']['clan_url'] + requests.utils.quote(config['INFO']['clan_tag']) + '/members'

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        logger.warning(f'Get clan member data returned {r.status_code}')
        return -1
    else:
        logger.info(f'Get clan member data returned {r.status_code}')

        timestamp = get_timestamp()
        date, time = str(timestamp).split(' ')

        file = f'{date}_{time[:5].replace(":", "-")}_{config["INFO"]["clan_name"]}_Members.json'
        file_path = Path(config['INFO']['data_folder'], 'Clan Members', file)
        content = r.json()
        content['timestamp'] = str(timestamp)
        with open(file_path, 'w') as f:
            json.dump(content, f, indent=2)

        if submit_to_database:
            insert_players_from_clan(parse_clan_members(file_path), verbose=True)

    return 0


def get_clan_war_data(submit_to_database):
    config = get_config('secrets.ini')
    headers = {'Accept': 'application/json', 'authorization': base64.b64decode(config['INFO']['api_token']).decode()}

    config = get_config('config.ini')
    url = config['INFO']['clan_url'] + requests.utils.quote(config['INFO']['clan_tag']) + '/currentwar'

    r = requests.get(url, headers=headers)
    logger.info(f'Get clan war data returned {r.status_code}')

    if r.status_code != 200:
        return -1
    else:
        content = r.json()
        logger.info(f'Clan war data has status of: {content["state"]}')

        if content['state'] != 'warEnded':
            print('War data not available at this time.')
        else:
            if get_recorded_status(str(content['start_time'])):
                print('This war has already been collected, aborting...')
            else:
                timestamp = get_timestamp()
                date, time = str(timestamp).split(' ')
                content['timestamp'] = str(timestamp)

                file = f'{date}_{time[:5].replace(":", "-")}_{format_name(content["clan"]["name"])}_War.json'
                file_path = Path(config['INFO']['data_folder'], 'Clan War', file)

                with open(file_path, 'w') as f:
                    json.dump(content, f, indent=2)

                if submit_to_database:
                    details, members, attacks = parse_clan_war_file(file_path)
                    insert_clan_war(details, members, attacks)


class ClanWar:
    def __init__(self, action, file_path=None):
        self.config = get_config('config.ini')
        self.file_path = file_path
        self.details = dict()
        self.members = list()
        self.attacks = list()
        self.status = True

        if action == 'get':
            self.get_data()
        elif action == 'pull':
            self.pull_data(self.file_path)
        else:
            pass

    def get_data(self):
        config = get_config('secrets.ini')
        headers = {'Accept': 'application/json', 'authorization': base64.b64decode(config['INFO']['api_token']).decode()}

        url = self.config['INFO']['clan_url'] + requests.utils.quote(self.config['INFO']['clan_tag']) + '/currentwar'

        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            self.status = False
        else:
            content = r.json()
            if content['state'] != 'warEnded':
                print('War data not available at this time.')
                self.status = False
                return -1
            else:
                if get_recorded_status(str(content['start_time'])):
                    self.status = False
                    print('This war has already been collected, aborting...')
                else:
                    timestamp = get_timestamp()
                    date, time = str(timestamp).split(' ')
                    content['timestamp'] = str(timestamp)

                    file = f'{date}_{time[:5].replace(":", "-")}_{format_name(content["clan"]["name"])}_ClanWar.json'
                    file_path = Path(self.config['INFO']['data_folder'], 'Clan War', file)

                    with open(file_path, 'w') as f:
                        json.dump(content, f, indent=2)

                    self.details, self.members, self.attacks = parse_clan_war_file(file_path)

    def pull_data(self, file_path):
        self.details, self.members, self.attacks = parse_clan_war_file(file_path)

    def submit_to_database(self):
        insert_clan_war(self)


class LeagueWar:
    def __init__(self, action):
        self.config = get_config('config.ini')
        self.details = dict()
        self.clans = list()
        self.wars = list()
        self.players = list()
        self.battles = list()
        self.status = True

        if action == 'get':
            self.get_data()
        elif action == 'pull':
            self.pull_data()
        else:
            pass

    def get_data(self):
        config = get_config('secrets.ini')
        headers = {'Accept': 'application/json', 'authorization': base64.b64decode(config['INFO']['api_token']).decode()}

        url = self.config['INFO']['clan_url'] + requests.utils.quote(
            self.config['INFO']['clan_tag']) + '/currentwar/leaguegroup'

        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            self.status = False
        else:
            content = r.json()

            self.details['league_season'] = content['season']

            content['timestamp'] = str(get_timestamp())

            folder = Path(self.config['INFO']['data_folder'], 'League War', content['season'])

            if not Path.is_dir(folder):
                Path.mkdir(folder)

            file = f'{content["season"]}_data.json'
            file_path = Path(folder, file)

            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2)

            self.clans, self.wars = parse_league_war_file(file_path)

            season_war_files = Path(self.config['INFO']['data_folder'], 'League War', content['season'], 'Wars')
            processed_wars = []
            if Path.is_dir(season_war_files):
                for root, dirs, files in os.walk(season_war_files):
                    for file in files:
                        war_tag = str(file)[10:20]

                        for pos, war in enumerate(self.wars):
                            if war['war_tag'] == war_tag:
                                war_data = self.wars.pop(pos)
                                processed_wars.append(war_tag)

                                new_war_data, league_players, league_battles = parse_war_file(Path(root, file), war_data)

                                self.wars.insert(pos, new_war_data)

                                for player in league_players:
                                    self.players.append(player)

                                for battle in league_battles:
                                    self.battles.append(battle)
                                break

            for pos, war in enumerate(self.wars):
                if war['war_tag'] not in processed_wars:
                    url = self.config['INFO']['clan_url'][:-6] + 'clanwarleagues/wars/' + requests.utils.quote(war['war_tag'])
                    headers = {'Accept': 'application/json',
                               'authorization': base64.b64decode(self.config['INFO']['token']).decode()}

                    r = requests.get(url, headers=headers)

                    if r.status_code == 200:
                        content = r.json()
                        if content['state'] == 'warEnded':
                            content['war_round'] = war['war_round']
                            content['war_tag'] = war['war_tag']
                            content['timestamp'] = str(get_timestamp())

                            folder = Path(self.config['INFO']['data_folder'], 'League War',
                                          self.details['league_season'], 'Wars')

                            if not Path.is_dir(folder):
                                Path.mkdir(folder)

                            file = f'{self.details["league_season"]}_{war["war_round"]}_{war["war_tag"]}.json'
                            file_path = Path(folder, file)

                            with open(file_path, 'w') as f:
                                json.dump(content, f, indent=2)

                            old_war_data = self.wars.pop(pos)

                            new_war_data, league_players, league_battles = parse_war_file(file_path, old_war_data)

                            self.wars.insert(pos, new_war_data)

                            for player in league_players:
                                self.players.append(player)

                            for battle in league_battles:
                                self.battles.append(battle)
                        else:
                            break
            self.flush_wars()

    def pull_data(self):
        file_path = find_file_options(Path(self.config['INFO']['data_folder'], 'League War'), False, 1)
        self.clans, self.wars = parse_league_war_file(file_path)
        self.details['league_season'] = self.clans[0]['league_season']

        war_folder = Path(self.config['INFO']['data_folder'], 'League War', self.details['league_season'], 'Wars')

        for root, dirs, files in os.walk(war_folder):
            for file in files:
                for pos, war in enumerate(self.wars):
                    war_tag = str(file)[10:20]
                    if war['war_tag'] == war_tag:
                        old_war_data = self.wars.pop(pos)
                        break
                new_war_data, league_players, league_battles = parse_war_file(Path(root, file), old_war_data)
                self.wars.insert(pos, new_war_data)

                for player in league_players:
                    self.players.append(player)

                for battle in league_battles:
                    self.battles.append(battle)
        self.flush_wars()

    def flush_wars(self):
        remove_list = []
        for war in self.wars:
            if len(war) == 4:
                remove_list.append(war)

        for war in remove_list:
            self.wars.remove(war)

    def submit_to_database(self):
        insert_league_war_data(self, verbose=True)


