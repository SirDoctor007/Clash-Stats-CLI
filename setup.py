import configparser
from pathlib import Path
from database_managment import create_database


def setup():
    config = configparser.ConfigParser()
    config.read(Path('Config', 'config.ini'))

    data_path = Path(config['INFO']['data_folder'])

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