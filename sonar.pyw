import main
import json
import httpx
import asyncio
from time import sleep
from winotify import Notification
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

        all_urls = [main.Arrays.base_url + data["relationships"][1]["id"] + '/feed' for key, data in Arrays.settings_dict.items()]
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url, follow_redirects=True, params=params) for url in all_urls)
            reqs = await asyncio.gather(*tasks)

        for req in reqs:
            for key, value in Arrays.settings_dict.items():
                if value["relationships"][1]["id"] == req.json()["data"][0]["relationships"][1]["id"]:
                    title = key
                    break
            ap_items = req.json()["data"][0]
            Arrays.updated_status.setdefault(title, ap_items)

    @staticmethod
    def toaster(series_title: str, ch_no: str, ch_title: str, ch_id: str) -> None:
        toast = Notification(
            app_id="MangaDex RSS",
            title=series_title,
            msg=f"Ch. {ch_no}: {ch_title}",
            launch=f"https://www.mangadex.org/chapter/{ch_id}"
        )
        toast.show()
        sleep(0.1)

    @staticmethod
    def update_checker() -> None:
        for title, data in Arrays.settings_dict.items():
            for key, value in Arrays.updated_status.items():
                if title == key:
                    old_time = dt.strptime(data["attributes"]["readableAt"], '%Y-%m-%dT%H:%M:%S%z')
                    new_time = dt.strptime(value["attributes"]["readableAt"], '%Y-%m-%dT%H:%M:%S%z')
                    ch_no = value["attributes"]["chapter"]
                    ch_title = value["attributes"]["title"]
                    ch_id = value["id"]
                    if old_time < new_time:
                        Guncs.toaster(title, ch_no, ch_title, ch_id)
                    else:
                        print(title, "wasn't updated")
                        #Arrays.updated_status.pop(key)
                    break

    @staticmethod
    def save_settings(new_settings: dict) -> None:
        Arrays.settings_dict.update(new_settings)

        with open(main.Guncs.resource_path('manga_notification_settings.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(Arrays.settings_dict, indent=4))


if __name__ == '__main__':
    Guncs.load_settings()
    asyncio.run(Guncs.sonar())
    Guncs.update_checker()
    Guncs.save_settings(Arrays.updated_status)
