import configparser
import logging.handlers
from pathlib import Path
from main_functions import get_config
from setup import setup

# If the database does not exist run the setup script
config = get_config('database.ini')
if not Path.is_file(Path(config['INFO']['database_name'])):
    setup()

# Sets up logging information
config = get_config('config.ini')
max_bytes = int(config['LOGGING']['max_bytes'])
backup_count = int(config['LOGGING']['backup_count'])
logging_level = config['LOGGING']['file_logging_level']

handler = [logging.handlers.RotatingFileHandler(Path('Logs', 'error.log'), maxBytes=max_bytes, backupCount=backup_count)]
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_datefmt = '%Y-%m-%d %H:%M:%S'

logging.basicConfig(level=logging_level, format=log_format, datefmt=log_datefmt, handlers=handler)
logger = logging.getLogger(__name__)


from data_collector import *
from data_viewer import *
from setup import setup


class Menu:
    def __init__(self):
        # self.main_menu()
        pass

    def main_menu(self):
        choices = [
            'Enter Data Viewer',
            'Enter Data Collector',
            'Enter Manual Entry',
            'Enter Database Management',
            'Quit'
        ]

        clear()
        banner = pyfiglet.figlet_format('Stats of Clash')
        print(banner)
        ans = get_answer(choices)

        if ans == 'Enter Data Viewer':
            self.data_viewer()
        elif ans == 'Enter Data Collector':
            self.data_collector()
        elif ans == 'Enter Manual Entry':
            self.manual_entry()
        elif ans == 'Enter Database Management':
            self.database_management()
        elif ans == 'Quit':
            quit()

    def data_viewer(self):
        choices = [
            'View Tracked Players',
            'View Clan Members',
            'View Recorded Clan Wars',
            'View Clan War',
            'View League War',
            'Go Back',
            'Quit'
        ]

        clear()
        banner = pyfiglet.figlet_format('Data Viewer')
        print(banner)

        ans = get_answer(choices)

        if ans == 'View Tracked Players':
            view_tracked_players()
        elif ans == 'View Clan Members':
            view_clan_members()
        elif ans == 'View Recorded Clan Wars':
            cw = ClanWarViewer()
            cw.view_recorded_clan_wars()
        elif ans == 'View Clan War':
            cw = ClanWarViewer()
            cw.view_clan_war()
        elif ans == 'View League War':
            view_league_war()
        elif ans == 'Go Back':
            self.main_menu()
        elif ans == 'Quit':
            quit()

        _ = input('\nPress Enter to Continue...')
        self.data_viewer()

    def data_collector(self):
        choices = [
            'Update Player\'s Records',
            'Get Player\'s Records via FTP',
            'Update Clan Members',
            'Get Clan War Data',
            'Get League War Data',
            'Go Back',
            'Quit'
        ]

        clear()
        banner = pyfiglet.figlet_format('Data Collector')
        print(banner)

        ans = get_answer(choices)

        if ans == 'Update Player\'s Records':
            pd = PlayerData('get')
            if pd.status:
                pd.submit_to_database()
        # TODO Remove the FTP option once I no longer need it. Not an intended function.
        elif ans == 'Get Player\'s Records via FTP':
            pd = PlayerData('get_ftp')
            if pd.status:
                pd.submit_to_database()
        elif ans == 'Update Clan Members':
            cm = ClanMembers('get')
            if cm.status:
                cm.submit_to_database()
        elif ans == 'Get Clan War Data':
            cw = ClanWar('get')
            if cw.status:
                cw.submit_to_database()
        elif ans == 'Get League War Data':
            lw = LeagueWar('get')
            if lw.status:
                lw.submit_to_database()
        elif ans == 'Go Back':
            self.main_menu()
        elif ans == 'Quit':
            quit()

        _ = input('\nPress Enter to Continue...')
        self.data_collector()

    def manual_entry(self):
        choices = [
            'Enter Player Record from json File',
            'Enter Clan War Data from json File',
            'Enter League War Data from json File',
            'Enter Clan Member Data from json File',
            'Go Back',
            'Quit'
        ]

        clear()
        banner = pyfiglet.figlet_format('Manual Entry')
        print(banner)

        ans = get_answer(choices)

        if ans == 'Enter Player Record from json File':
            files = find_file_options(Path('Data', 'Player'))
            for file in files:
                pd = PlayerData('pull', file)
                if pd.status:
                    pd.submit_to_database()
        elif ans == 'Enter Clan War Data from json File':
            files = find_file_options(Path('Data', 'Clan War'))
            for file in files:
                cw = ClanWar('pull', file)
                if cw.status:
                    cw.submit_to_database()
        elif ans == 'Enter League War Data from json File':
            lw = LeagueWar('pull')
            lw.submit_to_database()
        elif ans == 'Enter Clan Member Data from json File':
            file = find_file_options(Path('Data', 'Clan Members'), allow_multiple_options=False)
            cm = ClanMembers('pull', file_path=file)
            if cm.status:
                cm.submit_to_database()
        elif ans == 'Go Back':
            self.main_menu()
        elif ans == 'Quit':
            quit()

        _ = input('\nPress Enter to Continue...')
        self.manual_entry()

    def database_management(self):
        choices = [
            'Run Setup Script',
            'Create Database',
            'Update Tracked Players',
            'Remove a Clan War',
            'Go Back',
            'Quit'
        ]

        clear()
        banner = pyfiglet.figlet_format('DB Management')
        print(banner)

        ans = get_answer(choices)

        if ans == 'Run Setup Script':
            setup()
        elif ans == 'Create Database':
            create_database()
        elif ans == 'Update Tracked Players':
            update_tracked_players()
        elif ans == 'Remove a Clan War':
            remove_clan_war()
        elif ans == 'Go Back':
            self.main_menu()
        elif ans == 'Quit':
            quit()

        _ = input('\nPress Enter to Continue...')
        self.database_management()


if __name__ == '__main__':
    logging.basicConfig(filename='test.log', level=logging.DEBUG, format='%(levelname)s\t%(asctime)s\t%(message)s')

    menu = Menu()
    menu.main_menu()
