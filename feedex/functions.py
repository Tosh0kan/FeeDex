from .classes import *

import re
import pytz
import httpx
import asyncio
from time import sleep
from bs4 import BeautifulSoup
from winotify import Notification
from datetime import datetime as dt
from datetime import timedelta as td


def get_inital_manga_state(manga_urls: list = None, list_url: str = None) -> dict | list:
    """
    Requests the API the current state of the newly subscribed manga
    to populate the JSON.
    """
    async def manga_proccer(url_list) -> dict | list:
        if len(url_list) == 1:
            series_id = re.split(r'.+title/([^/]+).*', url_list[0])
            series_id = ''.join(series_id)
            series = httpx.get(
                f'https://api.mangadex.org/manga/{series_id}',
                follow_redirects=True
            )

            init_state = httpx.get(
                f'https://api.mangadex.org/manga/{series_id}/feed',
                follow_redirects=True,
                params={
                    # TODO change the configuration for preferred language
                    "translatedLanguage[]": "en",
                    "order[readableAt]": "desc"
                }
            ).json()["data"][0]

            series_title = series.json()['data']['attributes']["title"]["en"]

            return {series_title: init_state}

        else:
            title_urls = []
            feed_urls = []
            for url in url_list:
                series_id = re.split(r'.+title/([^/]+).*', url)
                series_id = ''.join(series_id)
                title_url = f'https://api.mangadex.org/manga/{series_id}'
                title_urls.append(title_url)
                feed_url = f'https://api.mangadex.org/manga/{series_id}/feed'
                feed_urls.append(feed_url)

            while len(feed_urls) > 0 and len(title_urls) > 0:
                async with httpx.AsyncClient() as client:
                    tasks = (client.get(url, follow_redirects=True, timeout=10) for url in title_urls)
                    title_reqs = await asyncio.gather(*tasks)

                async with httpx.AsyncClient() as client:
                    tasks = (client.get(url, follow_redirects=True, timeout=10) for url in feed_urls)
                    feed_reqs = await asyncio.gather(*tasks)

                init_states = []
                for title in title_reqs:
                    try:
                        if title.status_code == 200:
                            for feed in feed_reqs:
                                if title.json()["data"]["id"] == feed.json()["data"][0]["relationships"][1]["id"]:
                                    init_states.append({title.json()['data']['attributes']["title"]["en"]: feed.json()["data"][0]})
                                    title_urls.remove(str(title.url))
                                    feed_urls.remove(str(feed.url))
                                    break
                                else:
                                    continue
                        else:
                            continue
                    except IndexError:
                        title_urls.remove(str(title.url))
                        feed_urls.remove(str(feed.url))

            return init_states

    if manga_urls is not None:
        return asyncio.run(manga_proccer(manga_urls))

    else:
        procced_list_url = re.split(r'.+list/([^/]*).*', list_url)
        procced_list_url = ''.join(procced_list_url)
        list_ids = httpx.get(
            f'https://api.mangadex.org/list/{procced_list_url}',
            follow_redirects=True,
            timeout=10
        )
        list_ids = list_ids.json()["data"]["relationships"]
        list_ids = (e['id'] for e in list_ids)
        url_list = []
        for id in list_ids:
            url_list.append(f'https://mangadex.org/title/{id}/')
        return asyncio.run(manga_proccer(url_list[0:-1]))


async def sonar(settings_obj: Settings, mangas_registry: list) -> list:
    """
    The function that interacts with the API. Takes in the base instance of the Settings()
    class and the Mangas.registry_ to generate urls that will ping the api domain, generating
    a list with the dicts of all the chapters published since the last one.
    """
    all_urls = []
    for instance in mangas_registry:
        latest_date_dt = dt.strptime(instance.latest_date, '%Y-%m-%dT%H:%M:%S%z')
        latest_date_dt = latest_date_dt + td(seconds=1)
        latest_date = latest_date_dt.strftime('%Y-%m-%dT%H:%M:%S%z')

        url_ = f'https://api.mangadex.org/chapter?manga={instance.series_id}&publishAtSince={latest_date}&order[chapter]=desc'
        if instance.scan_group != "":
            url_ += '&groups[]=' + instance.scan_group
        for lang in settings_obj.settings["favLanguages"]:
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
            except IndexError:
                all_urls.remove(str(req.url))
            except Exception:
                continue

    output_ = [req.json()["data"] for req in reqs]
    new_output = []
    for series in output_:
        for chapter in series:
            new_output.append(chapter)
    sonar_echo = new_output
    return sonar_echo


def toaster(sonar_echo: list, mangas_registry: list) -> None:
    if len(sonar_echo) > 1:
        toast = Notification(
            app_id="FeeDex",
            title="Multiple Updates Inbound!",
            msg="Check your Actions Center for a full list!",
            duration="long"
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


def ping_jokey(sonar_echo: list, mangas_registry: list, settings_obj: Settings) -> None:
    """
    Takes in the sonar echo, the base instance of the Settings() class (usually just settings)
    and the Mangas.registry_ to process the sonar echo, generate the toasts if there are any new
    chapters, as well as update the Mangas() class instances inside registry_ and update the
    manga_subs.json file as well with the latest chapter.
    """
    if len(sonar_echo) > 0:
        toaster(sonar_echo, mangas_registry)
        skip_list = []
        for chapter in sonar_echo:
            for manga in mangas_registry:
                if manga.series_id in skip_list:
                    continue
                elif manga.series_id == chapter["relationships"][1]["id"]:
                    manga.update_instance(sonar_echo[sonar_echo.index(chapter)])
                    skip_list.append(manga.series_id)
                    update_dict = {manga.series_title: chapter}
                    if manga.scan_group == "":
                        update_dict[manga.series_title]["favGroup"] = ""
                        settings_obj.save_subs(manga_title=manga.series_title, manga_dict=update_dict)
                        break
                    else:
                        update_dict[manga.series_title]["favGroup"] = manga.scan_group
                        settings_obj.save_subs(manga_title=manga.series_title, manga_dict=update_dict)
                        break
    else:
        pass


def new_version_check(settings_obj, version) -> None:
    def get_latest_version() -> str:
        # TODO change all the names of this function so they are intuitive with repo_ver
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
            msg=f"Version {version} has been released.",
            launch=f"https://github.com/Tosh0kan/FeeDex/releases/tag/{version}"
        )
        toast.show()

    repo_ver = get_latest_version()
    bool_result = version_comparer(repo_ver, version)

    if bool_result:
        toaster(repo_ver)

    update_dict = {
        "metadata": {
            "lastCheck": str(dt.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'))
        }
    }
    settings_obj.save_settings(update_dict)
