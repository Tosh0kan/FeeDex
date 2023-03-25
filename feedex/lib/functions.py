from lib.__init__ import __version__
from lib.classes import *

import re
import pytz
import httpx
import asyncio
from time import sleep
from bs4 import BeautifulSoup
from winotify import Notification
from datetime import datetime as dt


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


async def sonar(settings_obj, mangas_registry: list) -> list:
    all_urls = []
    for instance in mangas_registry:
        latest_date = instance.latest_date.split('+')[0]
        url_ = f'https://api.mangadex.org/chapter?manga={instance.series_id}&publishAtSince={latest_date}&order[chapter]=desc'
        if instance.scan_group != "":
            url_ += '&groups[]=' + instance.scan_group
        for lang in settings_obj["favLanguages"]:
            url_ += f'&translatedLanguage[]={lang}'
        all_urls.append(url_)
    while len(all_urls) > 0:
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url, follow_redirects=True, timeout=10) for url in all_urls)
            reqs = await asyncio.gather(*tasks)

        output_ = []
        for req in reqs:
            try:
                if req.status_code == 200:
                    output_.append(req.json()["data"])
                    for instance in mangas_registry:
                        if instance.series_id == req.json()["data"][0]["relationships"][1]["id"]:
                            all_urls.remove(str(req.url))
                            break
                    else:
                        continue
            except Exception:
                continue

    output_ = [req.json()["data"] for req in reqs]
    new_output = []
    for series in output_:
        for chapter in series:
            if chapter == series[-1]:
                continue
            else:
                new_output.append(chapter)
    output_ = new_output
    return output_


def toaster(sonar_echo: list, mangas_registry: list) -> None:
    if len(sonar_echo) > 1:
        toast = Notification(
            app_id="FeeDex",
            title="Multiple Updates Inbound!",
            msg="Check your Actions Center for a full list!"
        )
        toast.show()
        sleep(0.20)

    for chapter in sonar_echo:
        for manga in mangas_registry:
            if chapter["relationships"][1]["id"] == manga.series_id:
                series_title = manga.series_title
        ch_no = chapter["attributes"]["chapter"]
        ch_title = chapter["attributes"]["title"]
        ch_id = chapter["id"]

        toast = Notification(
            app_id="FeeDex",
            title=f"{series_title}, Ch. {ch_no}",
            msg=f"{ch_title}",
            launch=f"https://www.mangadex.org/chapter/{ch_id}"
        )
        toast.show()
        sleep(0.20)

def new_version_check(settings_obj) -> None:
    def get_latest_version() -> str:
        while True:
            try:
                remote_ver = httpx.get('https://github.com/Tosh0kan/FeeDex/releases')
                break
            except Exception:
                sleep(1)
                continue
        active_page = BeautifulSoup(remote_ver.text, 'lxml')
        current_ver = active_page.find_all('h2', class_='sr-only')[0].text
        return current_ver

    def version_comparer(remote: str, local: str) -> bool:
        remote_split = remote.split('.')
        local_split = local.split('.')
        remote = int(''.join(remote_split))
        local = int(''.join(local_split))
        return remote > local

    def toaster(version: str) -> None:
        toast = Notification(
            app_id="FeeDex",
            title="FeeDex has been updated!",
            msg = f"Version {version} has been released.",
            launch=f"https://github.com/Tosh0kan/FeeDex/releases/tag/{version}"
        )
        toast.show

    repo_ver = get_latest_version()
    bool_result = version_comparer(repo_ver, __version__)

    if bool_result:
        toaster(repo_ver)

    update_dict = {
        "metadata": {
            "lastCheck": str(dt.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'))
        }
    }
    settings_obj.save_settings(update_dict)
