from lib.classes import *
from lib.functions import *

import os
import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPlainTextEdit, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QFormLayout, QDialog, QMainWindow, QWidget, QApplication, QCheckBox, QLabel, QScrollArea, QFrame


class AddSubWin(QDialog):
    """
    Logic for the subclass that spawns the QDialog for adding new subscriptions
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Subs...")
        self.setMinimumSize(QSize(500, 300))

        self.target_url = QPlainTextEdit()
        self.target_url.setPlaceholderText("Paste one or multiple manga's urls, each in a new line, or a list's url.")

        self.add_sub_button = QPushButton("Go")
        self.add_sub_button.clicked.connect(self.manga_init_state)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.add_sub_button)
        buttons_layout.setAlignment(Qt.AlignTop)

        layout = QHBoxLayout()
        layout.addWidget(self.target_url)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def manga_init_state(self):
        
        self.close()
        self.parent().setup()


class MngSubsWin(QDialog):
    """
    Logic for the subclass that spawns the QDialog for managing current subscriptions
    """
    def __init__(self, population, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Manage Subs...")
        self.button_state = 0
        self.inner_layout = QFormLayout()
        self.population = population

        for manga in population:
            checkbox = QCheckBox()
            checkbox.toggled.connect(lambda chk: self.button_state_change(chk))
            series_info = QLabel(f"{manga.series_title}")
            series_info.mousePressEvent = lambda event, cb=checkbox: cb.setChecked(not cb.isChecked())

            self.inner_layout.addRow(checkbox, series_info)

        self.inner_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.container_widget = QWidget()
        self.container_widget.setLayout(self.inner_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.container_widget)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.delete_button = QPushButton("Delete\nSubscriptions")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_subs)
        self.delete_button.setFixedSize(85, 45)
        self.delete_button_layout = QVBoxLayout()
        self.delete_button_layout.addWidget(self.delete_button)
        self.delete_button_layout.setAlignment(Qt.AlignTop)

        self.outer_layout = QHBoxLayout()
        self.outer_layout.addWidget(self.scroll_area)
        self.outer_layout.addLayout(self.delete_button_layout)

        # self.setMinimumSize(QSize(300, 24 * self.inner_layout.rowCount()))
        self.setLayout(self.outer_layout)

    def delete_subs(self):
        to_delete = []
        for row in range(self.inner_layout.rowCount()):
            checkbox = self.inner_layout.itemAt(row, QFormLayout.LabelRole).widget()
            if checkbox.isChecked():
                label = self.inner_layout.itemAt(row, QFormLayout.FieldRole).widget()
                to_delete.append(label)
        for widget in to_delete:
            for manga in Mangas.registry_:
                if manga.series_title == widget.text():
                    Mangas.registry_.remove(manga)
            self.inner_layout.removeRow(widget)
        self.close()

    def button_state_change(self, chk):
        if not self.delete_button.isEnabled():
            self.button_state += 1
        elif self.delete_button.isEnabled() and chk:
            self.button_state += 1
        elif self.delete_button.isEnabled() and not chk:
            self.button_state -= 1

        if self.button_state > 0:
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)


class FeeDexWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.first_time_check()
        self.setup()

    def setup(self):
        settings = Settings()
        for series, info in settings.subs.items():
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

    def first_time_check(self):
        subs_json_check = os.path.exists("./manga_subs_test.json")  # TODO change json before building
        settings_json_check = os.path.exists("./settings_test.json")  # TODO change json before building

        if not subs_json_check:
            with open('manga_subs_test.json', 'w') as f:
                f.write('{}')
        if not settings_json_check:
            with open('settings_test.json', 'w') as f:
                f.write('{}')



    def add_sub(self):
        add_win = AddSubWin(self)
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
