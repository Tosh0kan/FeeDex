from __init__ import *

import re
import pytz
import json
import httpx
import asyncio
from time import sleep
from bs4 import BeautifulSoup
from winotify import Notification
from datetime import datetime as dt
from datetime import timedelta as td


class Const:
    SETTINGS_DICT = {}


def load_settings() -> dict:
    #TODO change json before building
    with open('manga_notification_settings_test.json', 'r', encoding='utf-8') as f:
        Const.SETTINGS_DICT = json.loads(f.read())


def get_inital_manga_state(manga_url: str) -> dict:
    """
    Requests the API the current state of the newly subscribed manga
    to populate the JSON.
    """
    manga_id = re.split(r'.+title/([^/]+).+', manga_url)
    manga_id = ''.join(manga_id)
    title = httpx.get(
        f'https://api.mangadex.org/manga/{manga_id}',
        follow_redirects=True
    )

    init_state = httpx.get(
        f'https://api.mangadex.org/manga/{manga_id}/feed',
        follow_redirects=True,
        params={
            "translatedLanguage[]": "en",
            "order[readableAt]": "desc"
        }
    ).json()["data"][0]
    
    title = title.json()['data']['attributes']["title"]["en"]
    ch_no = init_state['attributes']['chapter']
    ch_title = init_state['attributes']['title']
    ch_id = init_state['id']
    latest_date = dt.strptime(init_state['attributes']['readableAt'], '%Y-%m-%dT%H:%M:%S%z')

    return title, ch_no, ch_title, ch_id, latest_date, {title: init_state}


def save_settings(first_time: bool = False, manga_dict: dict = None, update_only: bool = True, delete_entry: bool = False, manga_title: str = ''):
    """
        Creates the inner dicts in the settings JSON, and also creates the JSON proper
        in case it's the firt time using. It has options to only update previously subbed
        mangas with new info, add new subbed manga, as well as removing them.
    """
    meta_dict = {
            "metadata": {
                "version": __version__,
                "lastCheck": str(dt.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'))
            }
        }

    if first_time:
        Const.SETTINGS_DICT.update(manga_dict)
        Const.SETTINGS_DICT.update(meta_dict)

        with open('manga_notification_settings_test.json', 'r', encoding='utf-8') as f:
            f.write(json.dumps(Const.SETTINGS_DICT, indent=4))

    elif update_only:
        Const.SETTINGS_DICT.update(manga_dict)

        with open('manga_notification_settings_test.json', 'r', encoding='utf-8') as f:
            f.write(json.dumps(Const.SETTINGS_DICT, indent=4))

    elif delete_entry:
        Const.SETTINGS_DICT.pop(manga_title)

        with open('manga_notification_settings_test.json', 'r', encoding='utf-8') as f:
            f.write(json.dumps(Const.SETTINGS_DICT, indent=4))

    else:
        Const.SETTINGS_DICT.pop('metadata')
        Const.SETTINGS_DICT.update(manga_dict)
        Const.SETTINGS_DICT.update(meta_dict)

        with open('manga_notification_settings_test.json', 'r', encoding='utf-8') as f:
            f.write(json.dumps(Const.SETTINGS_DICT, indent=4))

load_settings()
print(Const.SETTINGS_DICT)
