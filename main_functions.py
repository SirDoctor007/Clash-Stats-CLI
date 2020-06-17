import base64
import configparser
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from string import printable

from PyInquirer import prompt


def find_file_options(folder, allow_multiple_options=True, recursive=10):

    file_options = dict()
    file_count = 1
    folder_depth = 0

    for root, dirs, files in os.walk(folder):
        for enu, file in enumerate(files):
            file_options[file_count] = Path(root, file)
            file_count += 1
        if recursive == folder_depth:
            break
        else:
            folder_depth += 1

    if allow_multiple_options:
        file_options[file_count] = 'All'

    files = []
    # User selects a file from the dictionary
    while True:
        try:
            for key in file_options.keys():
                print(f'{key}) {file_options[key]}')
            user_ans = int(input('Select a file to load: '))

            if user_ans in file_options.keys():
                if file_options[user_ans] == 'All':
                    del file_options[file_count]
                    for file in file_options.values():
                        files.append(file)
                    return files
                elif allow_multiple_options:
                    files.append(file_options[user_ans])
                    return files
                else:
                    return file_options[user_ans]
        except ValueError:
            print('Invalid number')


def get_config(config_file):
    config = configparser.ConfigParser()
    config.read(Path('Config', config_file))
    return config


def get_headers():
    config = get_config('secrets.ini')
    headers = {'Accept': 'application/json',
               'authorization': base64.b64decode(config['INFO']['api_token']).decode()}

    return headers


def get_answer(choices):
    choices_tuples = list()
    ans = None

    while True:
        for pos, choice in enumerate(choices, 1):
            print(f'{pos}) {choice}')
            choices_tuples.append((pos, choice))

        try:
            user_ans = int(input('--> '))
            for t in choices_tuples:
                if t[0] == user_ans:
                    ans = t[1]
            if ans is None:
                raise ValueError
            else:
                break
        except ValueError:
            print('That is not a valid answer.\n')

    return ans

def format_name(name):
    fname = ''
    for char in name:
        if char not in printable:
            fname += '#'
        else:
            fname += char
    return fname


def format_role(role):
    if role == 'leader':
        return 'Leader'
    elif role == 'coLeader':
        return 'Co-Leader'
    elif role == 'admin':
        return 'Elder'
    elif role == 'member':
        return 'Member'
    else:
        return 'N/A'


def convert_timestamp(timestamp):
    datetime_format = '%Y%m%dT%H%M%S.%fZ'
    return datetime.strptime(timestamp, datetime_format).replace(tzinfo=timezone.utc).astimezone(tz=None)


# Returns M-D-Y H:M from Y-M-D H:M:Sz
def format_timestamp(timestamp):
    datetime_obj = datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S%z')
    return datetime.strftime(datetime_obj, '%m-%d-%Y %H:%M')


def get_timestamp():
    timestamp_format = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(datetime.now().strftime(timestamp_format), timestamp_format).astimezone(tz=None)


def get_clan_war_file_hashes():
    config = configparser.ConfigParser()
    config.read('config.ini')

    folder = Path(config['DEFAULT']['data_folder'], 'Clan War')
    BLOCKSIZE = 175
    hashes = []

    for root, dir, files in os.walk(folder):
        for file in files:
            hasher = hashlib.md5()
            with open(Path(root, file), 'rb') as f:
                buf = f.read(BLOCKSIZE)
                hasher.update(buf)
            hashes.append(hasher.hexdigest())

    return hashes


def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def submit_to_database():
    question = [
        {
            'type': 'confirm',
            'message': 'Do you want to submit the data to the database?',
            'name': 'submit',
            'defualt': True
        }
    ]
    answer = prompt(question)

    return answer['submit']


# Used to add timestamp data to player json files that have already been collected
def update_player_files(folder):
    files = find_file_options(folder)
    for file in files:
        date, time, _ = str(file)[str(file).find('Player') + 7:].split('_')
        timestamp = date + ' ' + time.replace('-', ':') + ':00-4:00'
        print(timestamp)

        with open(file, 'r') as f:
            data = json.load(f)

        data['timestamp'] = timestamp

        with open(file, 'w') as f:
            json.dump(data, f, indent=2)


# class FindFiles:
#     def __init__(self):
#         self.allow_multiple_files = True
#         self.recursive = 100
#         self.file_options = dict()
#         self.file_count = 1
#         self.folder_depth = 0
#         self.message = ''
#
#     def get_files(self):
#         pass
#
#     def update_recursion(self, depth):
#         try:
#             depth = int(depth)
#         except ValueError:
#             pass
#         self.recursive = depth
#
#     def update_return(self, multi):
#         if type(multi) == bool:
#             self.allow_multiple_files = multi
