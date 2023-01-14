# ######################## To Do List ####################### #
# TODO Option to chance how often requests are made (maybe)  #
# ########################################################### #

import os
import sys
import re
import json
import httpx
import asyncio
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt


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
            with open(Guncs.resource_path(r'../manga_notification_settings.json'), 'r', encoding='utf-8') as f:
                settings_file = f.read()
            first_time_use = False

        except FileNotFoundError:
            first_time_use = True

    @staticmethod
    # TODO async for this funciton
    def get_inital_manga_status(manga_id: str):
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

        most_recent_date = dt.strptime(r_date.json()["data"][0]["attributes"]["readableAt"], '%Y-%m-%dT%H:%M:%S%z')

        return manga_title, most_recent_date

    @staticmethod
    def main():
        # TODO Finish menu
        # TODO Create functions for saving settings on a json file
        Guncs.get_initial_state()
        if first_time_use:
            first_time_menu = "Select one of the options:\n1. Add manga to subscription list\n\n"
            menu_choice = input(first_time_menu)

        else:
            regular_menu = "Select one of the options:\n1. Manage manga subscriptions\n2. Other options\n\n"
            menu_choice = input(regular_menu)

        if '1' in menu_choice:
            manga_url = input("Paste the URL of the manga's main page\n\n")
            manga_id = re.split(r'title/([^/]+)', manga_url)


if __name__ == '__main__':
    class Main:
        # TODO Think of a way to have multiple functions running cuncurrently
        while True:
            Guncs.main()
