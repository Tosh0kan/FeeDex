import os
import sys
import re
import json
import httpx


class Globals:
    global base_url
    base_url = 'https://api.mangadex.org/manga/'


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
                global settings_dict
                settings_dict = f.read()
            first_time_use = False

        except FileNotFoundError:
            first_time_use = True

    @staticmethod
    def get_inital_manga_state(manga_url: str):
        manga_id = re.split(r'.+title/([^/]+).+', manga_url)
        manga_id = ''.join(manga_id)
        r_title = httpx.get(
            f'{base_url}{manga_id}',
            follow_redirects=True
        )
        r_date = httpx.get(
            f'{base_url}{manga_id}/feed',
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
    def save_settings(manga_title: str, manga_id: str, most_recent_date: str):
        if first_time_use:
            settings_dict = {}
            settings_dict.setdefault(manga_title, []).append(manga_id), settings_dict.setdefault(manga_title, []).append(most_recent_date)

            with open(Guncs.resource_path('manga_notification_settings.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(settings_dict))

        else:
            with open(Guncs.resource_path('manga_notification_settings.json'), 'a', encoding='utf-8') as f:
                f.write(json.dumps(settings_dict))

    @staticmethod
    def main():
        Guncs.get_initial_state()
        if first_time_use:
            first_time_menu = "Select one of the options:\n1. Add manga subscription\n"
            menu_choice = input(first_time_menu)

            if '1' in menu_choice:
                while True:
                    manga_url = input("\nPaste the URL of the manga's main page\n")

                    if 'http' in manga_url:
                        manga_title, manga_id, most_recent_data = Guncs.get_inital_manga_state(manga_url)
                        Guncs.save_settings(manga_title, manga_id, most_recent_data)
                        break

                    else:
                        print('\nInvalid URL. Please, try again.\n')

            else:
                print("Invalid input. Please, try again.")

        else:
            main_menu = "\nSelect one of the options:\n1.  Add manga subscription\n2. Other options\n\n"
            menu_choice = input(main_menu)



if __name__ == '__main__':
    class Main:
        while True:
            Guncs.main()
