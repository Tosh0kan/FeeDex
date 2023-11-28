from libs.__init__ import __version__
from libs.classes import Settings, Mangas
from libs.dialogs import ErrorDialog, AddSubWin, MngSubsWin

import os
import sys
import json
import pytz
from datetime import datetime as dt
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QListView, QHBoxLayout, QVBoxLayout, QMainWindow, QWidget, QApplication, QScrollArea, QFrame


class FeeDexWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_check(__version__)
        self.setup()

    def setup(self):
        self.settings = Settings()
        Mangas.janny()
        for series, info in self.settings.subs.items():
            try:
                Mangas(series, info["relationships"][1]["id"], info["attributes"]["chapter"], info["attributes"]["title"], info["id"], info["attributes"]["publishAt"], info["favGroup"])
            except KeyError:
                Mangas(series, info["relationships"][1]["id"], info["attributes"]["chapter"], info["attributes"]["title"], info["id"], info["attributes"]["publishAt"])
        self.setWindowTitle("FeeDex Manager")
        self.setMinimumSize(QSize(800, 600))

        self.sub_button = QPushButton("Add subs...")
        self.sub_button.setFixedSize(85, 55)
        self.sub_button.clicked.connect(self.add_sub)

        self.unsub_button = QPushButton("Manage\nsubs...")
        self.unsub_button.setFixedSize(85, 55)
        self.unsub_button.clicked.connect(self.manage_subs)

        self.options_button = QPushButton("Options...")
        self.options_button.setFixedSize(85, 35)
        self.options_button.clicked.connect(self.manage_options)

        self.current_subs = QListView()

        self.view_layout = QHBoxLayout()
        self.view_layout.addWidget(self.current_subs)
        self.view_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.view_layout.setContentsMargins(1, 1, 1, 1)

        self.container_widget = QWidget()
        self.container_widget.setLayout(self.view_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.container_widget)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.sub_button)
        buttons_layout.addWidget(self.unsub_button)
        buttons_layout.addWidget(self.options_button)
        buttons_layout.setAlignment(Qt.AlignTop)

        parent_layout = QHBoxLayout()
        parent_layout.addWidget(self.scroll_area)
        parent_layout.addLayout(buttons_layout)

        container = QWidget()
        container.setLayout(parent_layout)

        self.setCentralWidget(container)

    def init_check(self, version):
        """
        Makes checks to see if the JSONs exist and are empty. If they don't exist,
        it creates it and writes an empty dicitionary in them or dummy settings,
        depending on the JSON. It checks if they are empty using a try/except
        block, and rewrites the empty dicitionary or dummy settings, again depending
        on the JSON. It also spawns an ErrorDialog window to inform that the user
        has no subs.
        """
        empty_subs = False
        empty_settings = False
        subs_json_check = os.path.exists("./manga_subs_test.json")  # TODO change json before building
        settings_json_check = os.path.exists("./settings_test.json")  # TODO change json before building

        settings_dict = {
            "metadata": {
                "version": version,
                "lastCheck": str(dt.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z'))
            },
            "favLanguages": ["en"]
        }

        if not subs_json_check:
            # TODO change json before building
            with open('manga_subs_test.json', 'w') as f:
                f.write('{}')
        if not settings_json_check:
            # TODO change json before building
            with open('settings_test.json', 'w') as f:
                f.write(json.dumps(settings_dict, indent=4))

        try:
            # TODO change json before building
            with open('manga_subs_test.json', 'r') as f:
                json.loads(f.read())
        except json.decoder.JSONDecodeError:
            # TODO change json before building
            with open('manga_subs_test.json', 'w') as f:
                f.write('{}')
                empty_subs = True
        try:
            # TODO change json before building
            with open('settings_test.json', 'r') as f:
                json.loads(f.read())
        except json.decoder.JSONDecodeError:
            # TODO change json before building
            with open('settings_test.json', 'w') as f:
                f.write(json.dumps(settings_dict, indent=4))
                empty_settings = True

        if empty_subs and empty_settings:
            error_window = ErrorDialog(2, 3, parent=self)
            error_window.exec()

        elif empty_subs:
            error_window = ErrorDialog(2, parent=self)
            error_window.exec()

        elif empty_settings:
            error_window = ErrorDialog(3, parent=self)
            error_window.exec()

    def add_sub(self):
        add_win = AddSubWin(self.settings, parent=self)
        add_win.exec()

    def manage_subs(self):
        mng_subs = MngSubsWin(Mangas.registry_, parent=self)
        mng_subs.exec()

    def manage_options(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FeeDexWindow()
    window.show()
    app.exec()
