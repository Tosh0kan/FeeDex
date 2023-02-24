import json
from winotify import Notification
from datetime import datetime as dt


class Mangas:
    registry_ = []

    def __init__(self, series: str, ch_no: str, ch_title: str, ch_id: str, latest_date: str):
        self.series = series
        self.ch_no = ch_no
        self.ch_title = ch_title
        self.ch_id = ch_id
        self.latest_date = latest_date
        Mangas.registry_.append(self)

    def __repr__(self) -> str:
        return "Manga('{}', '{}', '{}', '{}')".format(self.series, self.ch_no, self.ch_title, self.ch_id)


with open('manga_notification_settings.json', 'r') as f:
    settings_dict: dict = json.load(f)

for series, chapter in settings_dict.items():
    if series == 'metadata':
        continue
    else:
        Mangas(series, chapter['attributes']['chapter'], chapter['attributes']['title'], chapter['id'], dt.strptime(chapter['attributes']['readableAt'], '%Y-%m-%dT%H:%M:%S%z'))

for manga in Mangas.registry_:
    print(manga)
