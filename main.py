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


if __name__ == '__main__':
    logging.basicConfig(filename='test.log', level=logging.DEBUG, format='%(levelname)s\t%(asctime)s\t%(message)s')

    while True:
        questions = [
            {
                'type': 'list',
                'name': 'action',
                'message': 'What would you like to do?',
                'choices': [
                    'Enter Database Management',
                    'Enter Data Viewer',
                    'Update Player\'s Records',
                    'Get Player\'s Records via FTP',
                    'Update Clan Members',
                    'Get Clan War Data',
                    'Get League War Data',
                    'Quit'
                ]
            }
        ]
        clear()
        banner = pyfiglet.figlet_format('Stats of Clash')
        print(banner)
        answer = prompt(questions)

        if answer['action'] == 'Update Player\'s Records':
            get_player_data(submit_to_database())
        elif answer['action'] == 'Update Clan Members':
            get_clan_members(submit_to_database())
        elif answer['action'] == 'Get Player\'s Records via FTP':
            get_player_data_ftp(submit_to_database())
        elif answer['action'] == 'Get Clan War Data':
            cw = ClanWar('get')
            if cw.status:
                cw.submit_to_database()
        elif answer['action'] == 'Get League War Data':
            lw = LeagueWar('get')
            lw.submit_to_database()
        elif answer['action'] == 'Quit':
            quit()
        elif answer['action'] == 'Enter Data Viewer':
            while True:
                questions = [
                    {
                        'type': 'list',
                        'name': 'action',
                        'message': 'What would you like to do?',
                        'choices': [
                            'View Tracked Players',
                            'View Clan Members',
                            'View Clan War Attacks',
                            'View Player War Stats',
                            'View Recorded Clan Wars',
                            'View League War Round',
                            'Go Back'
                        ]
                    }
                ]

                clear()
                answer = prompt(questions)

                if answer['action'] == 'View Tracked Players':
                    view_tracked_players()
                elif answer['action'] == 'View Clan Members':
                    view_clan_members()
                elif answer['action'] == 'View Clan War Attacks':
                    view_war_stats()
                elif answer['action'] == 'View Player War Stats':
                    view_players_war_data()
                elif answer['action'] == 'View Recorded Clan Wars':
                    view_recorded_clan_wars()
                elif answer['action'] == 'View League War Round':
                    view_league_war_round()
                elif answer['action'] == 'Go Back':
                    break

                _ = input('\nPress Enter to Continue...')

        elif answer['action'] == 'Enter Database Management':
            while True:
                questions = [
                    {
                        'type': 'list',
                        'name': 'action',
                        'message': 'What would you like to do?',
                        'choices': [
                            'Run Setup Script',
                            'Create Database',
                            'Enter Player Record from json File',
                            'Enter Clan War Data from json File',
                            'Enter League War Data from json File',
                            'Enter Clan Member Data from json File',
                            'Update Tracked Players',
                            'Remove a Clan War',
                            'Go Back'
                        ]
                    }
                ]
                clear()
                answer = prompt(questions)

                if answer['action'] == 'Run Setup Script':
                    setup()
                elif answer['action'] == 'Create Database':
                    create_database()
                elif answer['action'] == 'Enter Player Record from json File':
                    files = find_file_options(Path('Data', 'Player'))
                    for file in files:
                        insert_player_record_data(parse_player_file(file), verbose=True)
                elif answer['action'] == 'Enter Clan War Data from json File':
                    files = find_file_options(Path('Data', 'Clan War'))
                    for file in files:
                        print(f'Inserting {file}...')
                        cw = ClanWar('pull', file)
                        cw.submit_to_database()
                        # details, members, attacks = parse_clan_war_file(file)
                        # insert_clan_war(details, members, attacks)
                elif answer['action'] == 'Enter League War Data from json File':
                    lw = LeagueWar('pull')
                    lw.submit_to_database()
                elif answer['action'] == 'Enter Clan Member Data from json File':
                    file = find_file_options(Path('Data', 'Clan Members'), allow_multiple_options=False)
                    insert_players_from_clan(parse_clan_members(file), verbose=True)
                elif answer['action'] == 'Update Tracked Players':
                    update_tracked_players()
                elif answer['action'] == 'Remove a Clan War':
                    remove_clan_war()
                elif answer['action'] == 'Go Back':
                    break

                _ = input('\nPress Enter to Continue...')
        if answer['action'] != 'Go Back':
            _ = input('\nPress Enter to Continue...')