import configparser
from pathlib import Path
from database_managment import create_database
from main_functions import get_config


def setup():
    config = get_config('config.ini')

    data_path = Path(config['INFO']['data_folder'])

    if Path.is_file(Path('Config', 'secrets.ini')):
        print('Secrets all ready exists')
    else:
        secret_config = configparser.ConfigParser()
        secret_config['INFO'] = {'api_token': ''}

        with open(Path('Config', 'secrets.ini'), 'w') as f:
            secret_config.write(f)

        print('Created secrets file. Be sure to populate it with your api token.')

    if Path.is_dir(data_path):
        print('Data exists')
    else:
        print('Creating Data folder')
        Path.mkdir(data_path)

    if Path.is_dir(Path(data_path / 'Clan Members')):
        print('Clan Members exists')
    else:
        Path.mkdir(Path(data_path / 'Clan Members'))
        print('Creating Clan Members folder')

    if Path.is_dir(Path(data_path / 'Clan War')):
        print('Clan War exists')
    else:
        Path.mkdir(Path(data_path / 'Clan War'))
        print('Creating Clan War folder')

    if Path.is_dir(Path(data_path / 'League War')):
        print('League War already exists')
    else:
        Path.mkdir(Path(data_path / 'League War'))
        print('Creating League War folder')

    if Path.is_dir(Path(data_path / 'Player')):
        print('Player exists')
    else:
        Path.mkdir(Path(data_path / 'Player'))
        print('Creating Player folder')

    create_database()