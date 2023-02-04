import main
import pytz
import json
import httpx
import asyncio
from time import sleep
from bs4 import BeautifulSoup
from winotify import Notification
from datetime import datetime as dt
from datetime import timedelta as td


# All arrays used in the program. Most functions don't have parameters nor
# return anything. Instead, they work by directly interacting with the arrays
# in this class.
class Arrays:
    settings_dict = {}
    updated_status = {}


class Guncs:
    @staticmethod
    def load_settings() -> None:
        with open(main.Guncs.resource_path('manga_notification_settings.json'), 'r', encoding='utf-8') as f:
            Arrays.settings_dict = json.loads(f.read())

    @staticmethod
    async def sonar() -> None:
        """
        This function requests data on the latest chapter for all subscribed manga, from the API
        and writes the info to the "updated_status" dictionary.
        """
        params = {
            "translatedLanguage[]": "en",
            "order[chapter]": "desc"
        }

        all_urls = [main.Arrays.base_url + data["relationships"][1]["id"] + '/feed' for key, data in Arrays.settings_dict.items() if "metadata" not in key]
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url, follow_redirects=True, params=params) for url in all_urls)
            reqs = await asyncio.gather(*tasks)

        # The inner loop gets the title of the manga from the API to use as the
        # key of the manga's key-value pair. The value is all data about the newest
        # chapter.
        for req in reqs:
            for key, value in Arrays.settings_dict.items():
                if value["relationships"][1]["id"] == req.json()["data"][0]["relationships"][1]["id"]:
                    title = key
                    break
            ap_items = req.json()["data"][0]
            Arrays.updated_status.setdefault(title, ap_items)

    @staticmethod
    def toaster(series_title: str, ch_no: str, ch_title: str, ch_id: str) -> None:
        """
        The toaster notification function.
        Key detail: DO NOT REMOVE OR CHANGE THE SLEEP FUNCTION. Otherwise,
        all the notifications may not spawn apropriately. Reason is unknown,
        but I assume it has something to do with the code's execution speed.
        """

        toast = Notification(
            app_id="MangaDex Feed",
            title=series_title,
            msg=f"Ch. {ch_no}: {ch_title}",
            launch=f"https://www.mangadex.org/chapter/{ch_id}"
        )
        toast.show()
        sleep(0.5)

    @staticmethod
    def new_ch_check() -> None:
        """
        Compares the information gotten from the API that was stored in the
        updated_status dict, with the base one retrieved from the settings JSON,
        stored in the settings_dict array. Furthermore, it also removes key-value
        pairs from mangas that haven't been updated, to be used by the save settings
        function.
        """

        for title, data in Arrays.settings_dict.items():
            for key, value in Arrays.updated_status.items():
                if title == key:
                    old_time = dt.strptime(data["attributes"]["readableAt"], '%Y-%m-%dT%H:%M:%S%z')
                    new_time = dt.strptime(value["attributes"]["readableAt"], '%Y-%m-%dT%H:%M:%S%z')
                    if old_time < new_time:
                        ch_no = value["attributes"]["chapter"]
                        ch_title = value["attributes"]["title"]
                        ch_id = value["id"]
                        Guncs.toaster(title, ch_no, ch_title, ch_id)
                    else:
                        Arrays.updated_status.pop(key)
                    break

    @staticmethod
    def save_settings(new_settings: dict) -> None:
        """
        It parses it updates the information already contained in the key-value
        pairs from the settings JSON. As it does not adds any new keys, only updates
        the values, the structure of the JSON is preserved.
        """

        Arrays.settings_dict.update(new_settings)

        with open(main.Guncs.resource_path('manga_notification_settings.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(Arrays.settings_dict, indent=4))

    @staticmethod
    def new_version_check() -> None:
        """
        Checks for new versions of this program, and updates the latest time it
        executed the check.
        """
        def get_latest_version() -> str:
            r_vers = httpx.get('https://github.com/Tosh0kan/MangaDexFeed/releases')
            active_page = BeautifulSoup(r_vers.text, 'lxml')
            current_version = active_page.find_all('h2', class_='sr-only')[0].text
            return current_version

        def version_comparer(remote: str, local: str) -> bool:
            remote_split = remote.split('.')
            local_split = local.split('.')
            remote = int(''.join(remote_split))
            local = int(''.join(local_split))

            return remote > local

        def toaster(version: str) -> None:
            toast = Notification(
                app_id="MangaDex Feed",
                title="MangaDex Feed has been updated!",
                msg=f"Version {version} has been released!",
                launch=f"https://github.com/Tosh0kan/MangaDexFeed/releases/tag/{version}"
            )
            toast.show()

        def update_metadata(cur_ver: str) -> None:
            meta_dict = {
                "metadata": {
                    "version": cur_ver,
                    "lastCheck": str(dt.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'))
                }
            }
            Guncs.save_settings(meta_dict)

        cur_ver = get_latest_version()
        bool_result = version_comparer(cur_ver, main.__version__)

        if bool_result:
            toaster(cur_ver)

        update_metadata(main.__version__)

    @staticmethod
    def main():
        sonar_timer = dt.now(pytz.utc)
        Guncs.load_settings()
        last_version_check = dt.strptime(Arrays.settings_dict["metadata"]["lastCheck"], '%Y-%m-%dT%H:%M:%S%z')
        asyncio.run(Guncs.sonar())

        while True:
            if dt.now(pytz.utc) >= sonar_timer + td(minutes=30):
                asyncio.run(Guncs.sonar())
                Guncs.new_ch_check()
                Guncs.save_settings(Arrays.updated_status)

            if dt.now(pytz.utc) >= last_version_check + td(days=30):
                Guncs.new_version_check()


if __name__ == '__main__':
    Guncs.main()
