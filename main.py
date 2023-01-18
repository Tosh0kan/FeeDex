import os
import sys
import re
import json
import httpx


class Arrays:
    base_url = 'https://api.mangadex.org/manga/'
    manga_list = []
    settings_dict = {}


class Guncs:
    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    @staticmethod
    def get_initial_state():
        global first_time_use
        try:
            with open(Guncs.resource_path('manga_notification_settings.json'), 'r', encoding='utf-8') as f:
                Arrays.settings_dict = json.loads(f.read())
            first_time_use = False

            for key in Arrays.settings_dict.keys():
                Arrays.manga_list.append(key)

        except FileNotFoundError:
            first_time_use = True

    @staticmethod
    def menu_structure():
        global first_time_use
        while True:
            if first_time_use:
                first_sub = input("\nSince this is your first time using the program, we need to start by adding your first manga to watch.\nPlease, paste the URL of the manga's main page\n\n")

                if 'http' in first_sub:
                    manga_title, manga_id, most_recent_date = Guncs.get_inital_manga_state(first_sub)
                    Guncs.save_settings(manga_title=manga_title, manga_id=manga_id, most_recent_date=most_recent_date)
                    first_time_use = False
                    return
                else:
                    print("Invalid URL. Please try again.\n")

            else:
                fst_menu_choice = input("\nChoose one of the options below:\n1. Add/Manage subscriptions\n\n")

                if '1' in fst_menu_choice:
                    print("\nCurrently subscribed mangas are:\n")
                    while True:
                        for manga in Arrays.manga_list:
                            print('\n', manga, sep='')
                        scnd_menu_choice = input(("\nChoose one of the options below:\n1. Add manga to subscriptions\n2. Remove manga from subscriptions\n3. Previous menu\n\n"))

                        if '1' in scnd_menu_choice and len(scnd_menu_choice) == 1:
                            manga_url = input("\nPlease, paste the URL of the manga's main page\n")
                            manga_title, manga_id, most_recent_date = Guncs.get_inital_manga_state(manga_url)
                            Guncs.save_settings(manga_title=manga_title, manga_id=manga_id, most_recent_date=most_recent_date)

                        elif '2' in scnd_menu_choice and len(scnd_menu_choice) == 1:
                            cnt = 0
                            for manga in Arrays.manga_list:
                                print('\n', cnt, '.', manga, sep='')
                                cnt += 1

                            while True:
                                delete_choice = input("\nChoose the manga you want to unsubscribe from\n")
                                try:
                                    delete_choice = int(delete_choice)
                                    _args = ['pop', Arrays.manga_list[delete_choice]]
                                    Guncs.save_settings(*_args)
                                    break

                                except ValueError:
                                    print("\nInvalid choice. Make sure you're choosing the option by typing in the according number\n")

                        elif '3' in scnd_menu_choice and len(scnd_menu_choice) == 1:
                            break
                        else:
                            print("\nInvalid input. Please try again.\n")
                else:
                    print("\nInvalid input. Please try again.\n")

    @staticmethod
    def get_inital_manga_state(manga_url: str):
        manga_id = re.split(r'.+title/([^/]+).+', manga_url)
        manga_id = ''.join(manga_id)
        r_title = httpx.get(
            f'{Arrays.base_url}{manga_id}',
            follow_redirects=True
        )
        r_date = httpx.get(
            f'{Arrays.base_url}{manga_id}/feed',
            follow_redirects=True,
            params={
                "translatedLanguage[]": "en",
                "order[chapter]": "desc"
            }
        )

        manga_title = r_title.json()['data']['attributes']["title"]["en"]

        most_recent_date = r_date.json()["data"][0]["attributes"]["readableAt"]

        return manga_title, manga_id, most_recent_date

    @staticmethod
    def save_settings(*args, manga_title: str = '', manga_id: str = '', most_recent_date: str = ''):
        if first_time_use:
            Arrays.settings_dict.setdefault(manga_title, []).append(manga_id)
            Arrays.settings_dict.setdefault(manga_title, []).append(most_recent_date)

            with open(Guncs.resource_path('manga_notification_settings.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(Arrays.settings_dict, indent=4))

        elif 'pop' in args:
            Arrays.manga_list.remove(args[1])
            for key in Arrays.settings_dict.keys():
                if args[1] in key:
                    Arrays.settings_dict.pop(key)
                    break

            with open(Guncs.resource_path('manga_notification_settings.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(Arrays.settings_dict, indent=4))

        else:
            new_sub = {}
            new_sub.setdefault(manga_title, []).append(manga_id)
            new_sub.setdefault(manga_title, []).append(most_recent_date)
            Arrays.settings_dict.update(new_sub)
            Arrays.manga_list.append(manga_title)

            with open(Guncs.resource_path('manga_notification_settings.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(Arrays.settings_dict, indent=4))

    @staticmethod
    def main():
        global first_time_use
        Guncs.get_initial_state()
        if first_time_use:
            Guncs.menu_structure()

        else:
            Guncs.menu_structure()


if __name__ == '__main__':
    class Main:
        while True:
            Guncs.main()
