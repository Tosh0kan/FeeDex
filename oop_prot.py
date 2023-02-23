import json


class Mangas:
    registry = []

    def __init__(self, series: str, ch_no: str, ch_title: str, ch_id: str):
        self.series = series
        self.ch_no = ch_no
        self.ch_title = ch_title
        self.ch_id = ch_id
        self.registry.append(self)

    def __repr__(self) -> str:
        return "Manga('{}', '{}', '{}', '{}')".format(self.series, self.ch_no, self.ch_title, self.ch_id)


with open('manga_notification_settings.json', 'r') as f:
    settings_dict: dict = json.load(f)

for series, chapter in settings_dict.items():
    if series == 'metadata':
        break
    else:
        Mangas(series, chapter['attributes']['chapter'], chapter['attributes']['title'], chapter['id'])
print(Mangas.registry[0].series)