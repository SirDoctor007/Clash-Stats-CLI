# import logging
# from data_collector import get_clan_war_data
# import pathlib
import pyfiglet
from setup import setup
# from PyInquirer import style_from_dict, Token, prompt, Separator
# from main_functions import find_file_options
# from database_managment import *
# from parse_json_file import *
from data_viewer import *
from data_collector import *
# import sqlite3


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
            'View Clan War Attacks',
            'View Player War Stats',
            'View Recorded Clan Wars',
            'View League War Round',
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
        elif ans == 'View Clan War Attacks':
            view_war_stats()
        elif ans == 'View Player War Stats':
            view_players_war_data()
        elif ans == 'View Recorded Clan Wars':
            view_recorded_clan_wars()
        elif ans == 'View League War Round':
            view_league_war_round()
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
            get_player_data(submit_to_database())
        # TODO Remove the FTP option once I no longer need it. Not an intended function.
        elif ans == 'Get Player\'s Records via FTP':
            get_player_data_ftp(submit_to_database())
        elif ans == 'Update Clan Members':
            get_clan_members(submit_to_database())
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
                insert_player_record_data(parse_player_file(file), verbose=True)
        elif ans == 'Enter Clan War Data from json File':
            files = find_file_options(Path('Data', 'Clan War'))
            for file in files:
                print(f'Inserting {file}...')
                cw = ClanWar('pull', file)
                cw.submit_to_database()
                details, members, attacks = parse_clan_war_file(file)
                insert_clan_war(details, members, attacks)
        elif ans == 'Enter League War Data from json File':
            lw = LeagueWar('pull')
            lw.submit_to_database()
        elif ans == 'Enter Clan Member Data from json File':
            file = find_file_options(Path('Data', 'Clan Members'), allow_multiple_options=False)
            insert_players_from_clan(parse_clan_members(file), verbose=True)
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
