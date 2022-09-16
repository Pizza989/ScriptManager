import math
import sys

from PyQt5.QtCore import Qt, QPoint, QEvent, QRect
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QSystemTrayIcon,
    QMessageBox,
    QMenu,
    QDesktopWidget,
)
from PyQt5 import uic  # type: ignore

from manager import start


class Popup(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("static/main.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.minimize_button.clicked.connect(self.hide)  # type: ignore
        self.resizing = False

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if math.sqrt(math.pow(self.width() - event.pos().x(), 2) + math.pow(self.height() - event.pos().y(), 2)) >= 28:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()


class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon) -> None:
        super().__init__(icon)

        self.menu = QMenu("BRUH")
        popup_action = self.menu.addAction("Show")
        popup_action.triggered.connect(self.run_popup)
        exit_action = self.menu.addAction("Exit")
        exit_action.triggered.connect(app.exit)

        self.setContextMenu(self.menu)
        self.activated.connect(self.on_tray_icon_activated)

    def run_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle("BNRUJH")
        x = msg.exec_()

    def on_tray_icon_activated(self, button):
        if button == 3:  # left-click
            self.run_popup()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    popup = Popup()

    icon = QSystemTrayIcon(QIcon("static/tray.ico"))

    menu = QMenu("ScriptManager")
    show_action = menu.addAction("Show...")
    show_action.triggered.connect(popup.show)
    hide_action = menu.addAction("Hide...")
    hide_action.triggered.connect(popup.hide)
    exit_action = menu.addAction("Exit...")
    exit_action.triggered.connect(app.exit)

    icon.setContextMenu(menu)
    icon.show()

    sys.exit(app.exec_())
