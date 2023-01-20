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

        Arrays.manga_list = [key for key, value in Arrays.settings_dict.items()]


    @staticmethod
    async def sonar():
        all_urls = [main.Arrays.base_url + id[0] + '/feed' for key, id in Arrays.settings_dict.items()]
        print(all_urls)
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url, follow_redirects=True) for url in all_urls)
            reqs = await asyncio.gather(tasks)
        pass
