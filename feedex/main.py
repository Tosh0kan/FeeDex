import os
import sys
import re
import pytz
import json
import httpx
from datetime import datetime as dt

__author__ = "Tosh0kan"
__version__ = "0.5.1"


class Arrays:
    base_url = 'https://api.mangadex.org/manga/'
    manga_list = []
    settings_dict = {}


class Guncs:
    @staticmethod
    def get_initial_state() -> None:
        """
        Checks if this is the first time using the program. Does it b checking the
        existence of the settings JSON and sets a global variable accordingly.
        """
        global first_time_use
        try:
            with open('manga_notification_settings.json', 'r', encoding='utf-8') as f:
                Arrays.settings_dict = json.loads(f.read())
            first_time_use = False

            for key in Arrays.settings_dict.keys():
                if "metadata" not in key:
                    Arrays.manga_list.append(key)

        except FileNotFoundError:
            first_time_use = True

    @staticmethod
    def menu_structure() -> None:
        """
        Menu structure. This is awful and I will remove it AS SOON as I figure
        out a better way to do it. If you have suggestions, by all means, give
        them to me.
        """
        global first_time_use
        while True:
            if first_time_use:
                first_sub = input("\nSince this is your first time using the program, we need to start by adding your first manga to watch.\nPlease, paste the URL of the manga's main page\n\n")

                if 'http' in first_sub:
                    manga_title, most_recent_chapter = Guncs.get_inital_manga_state(first_sub)
                    Guncs.save_settings(manga_title=manga_title, most_recent_chapter=most_recent_chapter)
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
                            manga_title, most_recent_chapter = Guncs.get_inital_manga_state(manga_url)
                            Guncs.save_settings(manga_title=manga_title, most_recent_chapter=most_recent_chapter)

                        elif '2' in scnd_menu_choice and len(scnd_menu_choice) == 1:
                            cnt = 0
                            for manga in Arrays.manga_list:
                                print('\n', cnt, '.', manga, sep='')
                                cnt += 1

                            while True:
                                delete_choice = input("\nChoose the manga you want to unsubscribe from\n")
                                try:
                                    delete_choice = int(delete_choice)
                                    if delete_choice <= cnt:
                                        _args = ['pop', Arrays.manga_list[delete_choice]]
                                        Guncs.save_settings(*_args)
                                        break

                                    else:
                                        print("\nInvalid choice. Make sure you're choosing the option by typing in the according number\n")

                                except ValueError:
                                    print("\nInvalid choice. Make sure you're choosing the option by typing in the according number\n")

                        elif '3' in scnd_menu_choice and len(scnd_menu_choice) == 1:
                            break
                        else:
                            print("\nInvalid input. Please try again.\n")
                else:
                    print("\nInvalid input. Please try again.\n")

    @staticmethod
    def get_inital_manga_state(manga_url: str) -> tuple:
        """
        Creates the settings JSON in case it doesn't exist yet, and requests
        the API the current state of the subscribed manga to populate the JSON.
        """
        manga_id = re.split(r'.+title/([^/]+).+', manga_url)
        manga_id = ''.join(manga_id)
        r_title = httpx.get(
            f'{Arrays.base_url}{manga_id}',
            follow_redirects=True
        )
        r_data = httpx.get(
            f'{Arrays.base_url}{manga_id}/feed',
            follow_redirects=True,
            params={
                "translatedLanguage[]": "en",
                "order[chapter]": "desc"
            }
        )
    
        manga_title = r_title.json()['data']['attributes']["title"]["en"]

        most_recent_chapter = r_data.json()["data"][0]

        return manga_title, most_recent_chapter

    @staticmethod
    def save_settings(*args, manga_title: str = '', most_recent_chapter: dict = None) -> None:
        """
        Creates the inner dicts in the settings JSON. Has options for removing
        them as well by passing the string 'pop' and the key of the dictionary
        to be removed as star arguments.
        """
        meta_dict = {
            "metadata": {
                "version": __version__,
                "lastCheck": str(dt.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'))
            }
        }

        if first_time_use:
            Arrays.settings_dict.setdefault(manga_title, most_recent_chapter)
            Arrays.settings_dict.update(meta_dict)

            with open('manga_notification_settings.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(Arrays.settings_dict, indent=4))

        elif 'pop' in args:
            Arrays.manga_list.remove(args[1])
            for key in Arrays.settings_dict.keys():
                if args[1] in key:
                    Arrays.settings_dict.pop(key)
                    break

            with open('manga_notification_settings.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(Arrays.settings_dict, indent=4))

        else:
            Arrays.settings_dict.pop("metadata")
            new_sub = {}
            new_sub.setdefault(manga_title, most_recent_chapter)
            Arrays.settings_dict.update(new_sub)
            Arrays.settings_dict.update(meta_dict)
            Arrays.manga_list.append(manga_title)

            with open('manga_notification_settings.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(Arrays.settings_dict, indent=4))

    @staticmethod
    def main() -> None:
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
