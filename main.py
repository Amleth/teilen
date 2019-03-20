from pathlib import PurePath
from PySide2 import QtGui
from PySide2.QtCore import QDir, QFile, QIODevice, Qt, QTextStream, Signal
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
)
from PySide2.QtCore import Slot, Qt
import random
import re
import signal
import string
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)

FONT_FAMILY = "Menlo"
FONT_SIZE = 14
MENLO_14_CHARACTER_WIDTH = 8
WIDEST_CHARACTER = "W"


class MyQPlainTextEdit(QPlainTextEdit):
    def keyPressEvent(self, event):
        if event.key() == 16777219:  # delete previous character
        	pass
        elif event.key() == 16777223:  # delete next character
            pass
        else:
            super().keyPressEvent(event)


class App(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.current_file = None
        self.last_opened_directory = QDir.homePath()

        #
        # Stylesheet
        #

        self.setStyleSheet(
            """
        QPlainTextEdit, QLabel {
            font-family: Menlo;
            font-size: {FONT_SIZE}px;
        }
        QFrame {
            border: 0px solid rgba(0, 0, 0, 0.1);
        }
        """
        )

        #
        # Widgets
        #

        # The editor
        self.plaintexteditor = MyQPlainTextEdit()

        # A glimpse of the begining & the end of the selection
        self.selection_start = QLabel("—")
        self.selection_start.setTextFormat(Qt.PlainText)
        self.selection_end = QLabel("—")
        self.selection_end.setTextFormat(Qt.PlainText)

        # Markup buttons bar
        self.buttons_bar = QWidget()
        self.buttons_bar.layout = QHBoxLayout()
        self.buttons_bar.setLayout(self.buttons_bar.layout)
        self.button_div = QPushButton("<div>")
        self.buttons_bar.layout.addWidget(self.button_div)

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget.layout)
        self.central_widget.layout.addWidget(self.selection_start)
        self.central_widget.layout.addWidget(self.selection_end)
        self.central_widget.layout.addWidget(self.buttons_bar)
        self.central_widget.layout.addWidget(self.plaintexteditor)

        #
        # Actions
        #

        self.open_action = QAction(
            "&Open", self, shortcut="Ctrl+O", statusTip="Open", triggered=self.open_file
        )
        self.save_action = QAction(
            "&Save", self, shortcut="Ctrl+S", statusTip="Save", triggered=self.save_file
        )
        self.exit_action = QAction(
            "&Tschüss",
            self,
            shortcut="Ctrl+Q",
            statusTip="Exit the application",
            triggered=self.close,
        )

        #
        # Menus
        #

        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.exit_action)

        #
        # Signals
        #

        self.plaintexteditor.selectionChanged.connect(self.selectionChanged)
        self.button_div.clicked.connect(self.insertDiv)

    def resizeEvent(self, event):
        pass

    @Slot()
    def selectionChanged(self):
        c = self.plaintexteditor.textCursor()
        s = c.selection().toPlainText()

        if len(s) > 0:
            selection_start_number_of_displayable_characters = (
                self.selection_start.width() // 8 - 2  # because of leading "… "
            )
            start_string_fragment = s[:selection_start_number_of_displayable_characters]
            start_string_fragment = " ".join(start_string_fragment.split())
            self.selection_start.setText(start_string_fragment + " …")

            selection_end_number_of_displayable_characters = (
                self.selection_end.width() // 8 - 2  # because of trailing "… "
            )
            end_string_fragment = s[-selection_end_number_of_displayable_characters:]
            end_string_fragment = " ".join(end_string_fragment.split())
            self.selection_end.setText("… " + end_string_fragment)
        else:
            self.selection_start.setText("—")
            self.selection_end.setText("—")

    @Slot()
    def insertDiv(self):
        c = self.plaintexteditor.textCursor()
        s = c.selection().toPlainText()
        if len(s) != 0:
            c.insertText("<div>" + s + "</div>")

    def open_file(self):
        filename, filtr = QFileDialog.getOpenFileName(
            self, dir=self.last_opened_directory
        )
        selected_file = QFile(filename)
        self.last_opened_directory = str(PurePath(str(selected_file)).parent)
        if selected_file.open(QFile.ReadOnly):
            self.current_file = filename
            content = QTextStream(selected_file).readAll()
            selected_file.close()
            self.plaintexteditor.document().setPlainText(content)

    def save_file(self):
        if self.current_file is not None:
            file = QFile(self.current_file)
            if not file.open(QIODevice.WriteOnly | QIODevice.Text):
                return
            out = QTextStream(file)
            out << self.plaintexteditor.document().toPlainText()
            file.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = App()
    widget.setWindowTitle("IReMus Teizer")
    widget.resize(1111, 888)
    widget.show()

    sys.exit(app.exec_())
