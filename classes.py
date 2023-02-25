from .__init__ import __version__

import pytz
import json
from datetime import datetime as dt


class Settings:
    def __init__(self):
        self.dict = Settings.load_settings(self)

    def load_settings(self) -> dict:
        # TODO change json before building
        with open('manga_notification_settings_test.json', 'r', encoding='utf-8') as f:
            settings_dict = json.loads(f.read())

        return settings_dict

    def save_settings(self: dict, manga_title: str = '', manga_dict: dict = None, first_time: bool = False, update_only: bool = True, delete_entry: bool = False):
        """
            Creates the inner dicts in the settings JSON, and also creates the JSON proper
            in case it's the firt time using. It has options to only update previously subbed
            mangas with new info, add new subbed manga, as well as removing them.
        """
        meta_dict = {
            "metadata": {
                "version": __version__,
                "lastCheck": str(dt.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'))
            }
        }

        if first_time:
            self.dict.update(manga_dict)
            self.dict.update(meta_dict)

        # TODO change json before building
            with open('manga_notification_settings_test.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.dict, indent=4))

        elif update_only:
            self.dict.update(manga_dict)

        # TODO change json before building
            with open('manga_notification_settings_test.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.dict, indent=4))

        elif delete_entry:
            self.dict.pop(manga_title)

        # TODO change json before building
            with open('manga_notification_settings_test.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.dict, indent=4))

        else:
            self.dict.pop('metadata')
            self.dict.update(manga_dict)
            self.dict.update(meta_dict)

        # TODO change json before building
            with open('manga_notification_settings_test.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.dict, indent=4))


class Mangas:
    registry_ = []

    def __init__(self, series: str, ch_no: str, ch_title: str, ch_id: str, latest_date: dt):
        self.series = series
        self.ch_no = ch_no
        self.ch_title = ch_title
        self.ch_id = ch_id
        self.latest_date = latest_date
        Mangas.registry_.append(self)

    def __repr__(self) -> str:
        return "Manga('{}', '{}', '{}', '{}')".format(self.series, self.ch_no, self.ch_title, self.ch_id)

    def __str__(self) -> str:
        return "{}, Latest Upload: Ch {}, {}, {}".format(self.series, self.ch_no, self.ch_title, self.latest_date)

    def update_instance(self, ch_no: str, ch_title: str, ch_id: str, latest_date: dt):
        self.ch_no = ch_no
        self.ch_title = ch_title
        self.ch_id = ch_id
        self.latest_date = latest_date
