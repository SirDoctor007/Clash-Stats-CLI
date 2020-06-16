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
