from .__init__ import __version__
from .classes import *

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


def get_inital_manga_state(manga_url: str) -> tuple[str, str, str, str, dt, dict]:
    """
    Requests the API the current state of the newly subscribed manga
    to populate the JSON.
    """
    manga_id = re.split(r'.+title/([^/]+).+', manga_url)
    manga_id = ''.join(manga_id)
    series = httpx.get(
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

    series = series.json()['data']['attributes']["title"]["en"]
    ch_no = init_state['attributes']['chapter']
    ch_title = init_state['attributes']['title']
    ch_id = init_state['id']
    latest_date = dt.strptime(init_state['attributes']['readableAt'], '%Y-%m-%dT%H:%M:%S%z')

    return series, ch_no, ch_title, ch_id, latest_date, {series: init_state}


def get_initial_pop(settings_dict: dict) -> None:
    for series, chapter in settings_dict.items():
        if series == 'metadata':
            continue

        else:
            Mangas(series, chapter['attributes']['chapter'], chapter['attributes']['title'], chapter['id'], dt.strptime(chapter['attributes']['readableAt'], '%Y-%m-%dT%H:%M:%S%z'))