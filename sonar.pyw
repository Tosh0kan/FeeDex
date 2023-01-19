import os
import sys
import json
import httpx
import asyncio
from plyer import notification
from datetime import datetime as dt
from datetime import timedelta as td


class Arrays:
    manga_ids = []
    manga_urls = ['https://api.mangadex.org/manga/{}'.format(id) for id in manga_ids]


class Guncs:
    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    @staticmethod
    def load_settings():  # TEST Test this function
        with open(Guncs.resource_path('manga_notification_settings.json'), 'r', encoding='utf-8') as f:
            loaded_settings = json.loads(f.read())
            Arrays.manga_ids = [value[0] for key, value in loaded_settings.items()]
