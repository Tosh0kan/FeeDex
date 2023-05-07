from lib.__init__ import __version__

import pytz
import json
from datetime import datetime as dt


class Settings:
    def __init__(self):
        self.settings: dict = Settings.load_settings(self)
        self.subs: dict = Settings.load_subs(self)

    def load_settings(self) -> dict:
        # TODO change json before building
        with open('settings_test.json', 'r', encoding='utf-8') as f:
            settings_dict = json.loads(f.read())

        return settings_dict

    def load_subs(self) -> dict:
        # TODO change json before building
        with open('manga_subs_test.json', 'r', encoding='utf-8') as f:
            manga_subs = json.loads(f.read())

        return manga_subs

    def save_settings(self, update_dict: dict, lang_pref: str = None):
        # TODO add method to remove favLanguages
        settings_dict = {
            "metadata": {
                "version": __version__,
                "lastCheck": str(dt.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'))
            },
            "favLanguages": ["en"]
        }
        if lang_pref is not None:
            settings_dict['favLanguages'].append(lang_pref)
        settings_dict.update(update_dict)
        self.settings.update(settings_dict)

        with open('settings_test.json', 'w') as f:
            f.write(json.dumps(self.settings, indent=4))

    def save_subs(self, manga_title: str = None, manga_dict: dict = None, preferr_group: str = None, first_time: bool = False, update: bool = True, delete_entry: bool = True):
        if first_time:
            # TEST vvvvvvvvvv
            for key in manga_dict.keys():
                manga_dict[key].update({'favGroup': ""})
                if preferr_group is not None:
                    manga_dict[key]["favGroup"] = preferr_group
            # TEST ^^^^^^^^^^
            self.subs.update(manga_dict)

        # TODO change json before building
            with open('manga_subs_test.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.subs, indent=4))

        elif update:
            if preferr_group is not None:
                for key in manga_dict.keys():
                    if key == manga_title:
                        # manga_dict[key].update({'favGroup': []})
                        manga_dict[key]["favGroup"] = preferr_group
                        break

            else:
                self.subs.update(manga_dict)

        # TODO change json before building
            with open('manga_subs_test.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.subs, indent=4))

        elif delete_entry:
            self.subs.pop(manga_title)

        # TODO change json before building
            with open('manga_subs_test.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.subs, indent=4))


class Mangas:
    registry_ = []

    def __init__(self, series_title: str, series_id: str, ch_no: str, ch_title: str, ch_id: str, latest_date: str, scan_group: str = ''):
        self.series_title = series_title
        self.series_id = series_id
        self.ch_no = ch_no
        self.ch_title = ch_title
        self.ch_id = ch_id
        self.scan_group = scan_group
        self.latest_date = latest_date
        Mangas.registry_.append(self)

    def __repr__(self) -> str:
        return "Manga('{}','{}', '{}', '{}', '{}', '{}', '{}')".format(self.series_title, self.series_id, self.ch_no, self.ch_title, self.ch_id, self.scan_group, self.latest_date)

    def __str__(self) -> str:
        return "{}, Latest Upload: Ch {}, {}, {}".format(self.series_title, self.ch_no, self.ch_title, self.latest_date)

    def update_instance(self, sonar_echo: dict):
        self.ch_no = sonar_echo["attributes"]["chapter"]
        self.ch_title = sonar_echo['attributes']["title"]
        self.ch_id = sonar_echo["id"]
        self.latest_date = sonar_echo["attributes"]["publishAt"]
