import main
import json
import httpx
import asyncio
import pytz
from plyer import notification
from datetime import datetime as dt
from datetime import timedelta as td


class Arrays:
    settings_dict = {}
    manga_list = []
    updated_status = {}


class Guncs:
    @staticmethod
    def load_settings() -> None:
        with open(main.Guncs.resource_path('manga_notification_settings.json'), 'r', encoding='utf-8') as f:
            Arrays.settings_dict = json.loads(f.read())

        # Arrays.manga_list = [key for key, value in Arrays.settings_dict.items()]

    @staticmethod
    async def sonar() -> None:
        params = {
            "translatedLanguage[]": "en",
            "order[chapter]": "desc"
        }

        all_urls = [main.Arrays.base_url + id[0] + '/feed' for key, id in Arrays.settings_dict.items()]
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url, follow_redirects=True, params=params) for url in all_urls)
            reqs = await asyncio.gather(*tasks)

        for req in reqs:
            for key, value in Arrays.settings_dict.items():
                if value[0] == req.json()["data"][0]["relationships"][1]["id"]:
                    title = key
                    break
            ap_items = req.json()["data"][0]
            Arrays.updated_status.setdefault(title, ap_items)

    @staticmethod
    def date_comparer() -> None:
        for title, list in Arrays.settings_dict.items():
            for key, value in Arrays.updated_status.items():
                if title == key:
                    old_time = dt.strptime(list[1], '%Y-%m-%dT%H:%M:%S%z')
                    new_time = dt.strptime(value["attributes"]["readableAt"], '%Y-%m-%dT%H:%M:%S%z')
                    if old_time < new_time:
                        print(title, "has updated")
                    else:
                        print(title, "has not updated")
                    break


if __name__ == '__main__':
    Guncs.load_settings()
    asyncio.run(Guncs.sonar())
    Guncs.manga_status_checker()
