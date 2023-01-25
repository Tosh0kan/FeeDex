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
    updated_status = {}


class Guncs:
    @staticmethod
    def load_settings():
        with open(main.Guncs.resource_path('manga_notification_settings.json'), 'r', encoding='utf-8') as f:
            Arrays.settings_dict = json.loads(f.read())

        Arrays.manga_list = [key for key, value in Arrays.settings_dict.items()]

    @staticmethod
    async def sonar():
        params = {
            "translatedLanguage[]": "en",
            "order[chapter]": "desc"
        }

        all_urls = [main.Arrays.base_url + id[0] + '/feed' for key, id in Arrays.settings_dict.items()]
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url, follow_redirects=True, params=params) for url in all_urls)
            reqs = await asyncio.gather(*tasks)

        list_id = 0
        for req in reqs:
            title = Arrays.manga_list[list_id]
            ap_items = req.json()["data"][0]
            Arrays.updated_status.setdefault(title, ap_items)
            list_id += 1


if __name__ == '__main__':
    Guncs.load_settings()
    asyncio.run(Guncs.sonar())
    with open(main.Guncs.resource_path('_sonar_test.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(Arrays.updated_status, indent=4))
