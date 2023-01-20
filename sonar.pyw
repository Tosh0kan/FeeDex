import main
import json
import httpx
import asyncio
from plyer import notification
from datetime import datetime as dt
from datetime import timedelta as td


class Arrays:
    settings_dict = {}
    manga_list = []


class Guncs:
    @staticmethod
    def load_settings():
        with open(main.Guncs.resource_path('manga_notification_settings.json'), 'r', encoding='utf-8') as f:
            Arrays.settings_dict = json.loads(f.read())


    @staticmethod
    async def sonar():
        pass
