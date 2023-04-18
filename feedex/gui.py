import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPlainTextEdit, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QFormLayout, QDialog, QMainWindow, QWidget, QApplication, QCheckBox, QLabel, QScrollArea


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
        print(self.target_url.toPlainText())


class MngSubsWin(QDialog):
    """
    Logic for the subclass that spawns the QDialog for managing current subscriptions
    """
    def __init__(self, num, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Manage Subs...")

        lorem_ipsum = [
            "Lorem ipsum dolor sit amet",
            "consectetur adipiscing elit",
            "Sed venenatis, ex nec euismod dignissim",
            "neque eros molestie nunc, nec fermentum",
            "massa arcu quis enim",
            "Nullam vestibulum vehicula",
            "metus ut volutpat",
            "Morbi pretium felis ut leo eleifend"
            "eget porttitor nunc sollicitudin",
            "Fusce ac tincidunt elit"
        ]

        self.inner_layout = QFormLayout()

        for e in range(num):
            self.checkbox = QCheckBox()
            self.series_info = QLabel(lorem_ipsum[e])
            self.inner_layout.addRow(self.checkbox, self.series_info)

        self.inner_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.container_widget = QWidget()
        self.container_widget.setLayout(self.inner_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.container_widget)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.delete_button = QPushButton("Delete\nSubscriptions")
        self.delete_button.clicked.connect(self.delete_subs)
        self.delete_button.setFixedSize(85, 45)
        self.delete_button_layout = QVBoxLayout()
        self.delete_button_layout.addWidget(self.delete_button)
        self.delete_button_layout.setAlignment(Qt.AlignTop)

        self.outer_layout = QHBoxLayout()
        self.outer_layout.addWidget(self.scroll_area)
        self.outer_layout.addLayout(self.delete_button_layout)

        self.setMinimumSize(QSize(300, 24 * self.inner_layout.rowCount()))
        self.setLayout(self.outer_layout)

    def delete_subs(self):
        to_delete = []
        for row in range(self.inner_layout.rowCount()):
            checkbox = self.inner_layout.itemAt(row, QFormLayout.LabelRole).widget()
            if checkbox.isChecked():
                label = self.inner_layout.itemAt(row, QFormLayout.FieldRole).widget()
                to_delete.append(label)
        self.close()


class FeeDexWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FeeDex Manager")
        self.setMinimumSize(QSize(800, 600))

        self.sub_button = QPushButton("Add subs...")
        self.sub_button.setFixedSize(85, 55)
        self.sub_button.clicked.connect(self.add_sub)

        self.unsub_button = QPushButton("Manage\nsubs...")
        self.unsub_button.setFixedSize(85, 55)
        self.unsub_button.clicked.connect(self.manage_subs)

        self.options_button = QPushButton("Options...")
        self.options_button.setFixedSize(85, 55)
        self.options_button.clicked.connect(self.manage_options)

        self.current_subs = QListView()

        self.view_layout = QHBoxLayout()
        self.view_layout.addWidget(self.current_subs)
        self.view_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.container_widget = QWidget()
        self.container_widget.setLayout(self.view_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.container_widget)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

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

    def add_sub(self):
        add_win = AddSubWin(self)
        add_win.exec()

    def manage_subs(self):
        mng_subs = MngSubsWin(9, self)
        mng_subs.exec()

    def manage_options(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FeeDexWindow()
    window.show()
    app.exec()
