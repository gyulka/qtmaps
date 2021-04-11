import sys

import requests
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

Ui_MainWindown, _ = uic.loadUiType('uis/untitled.ui')

# --------константы


static_server = 'https://static-maps.yandex.ru/1.x/'
geocode_key = "40d1649f-0493-4b70-98ba-98533de7710b"
geocode_server = "https://geocode-maps.yandex.ru/1.x/"
l = ['map', 'sat', 'sat,skl']


# ---------/константы


class Dot:
    def __init__(self, a, b):
        self.a, self.b = a, b

    def __str__(self):
        return f'{self.a},{self.b}'

    def __iadd__(self, other):
        self.a += other[0]
        self.b += other[1]
        if not (0 <= self.a <= 180):
            self.a = (self.a + 180) % 180
        if not (0 <= self.b <= 180):
            self.a = (self.b + 180) % 180
        return self


class Ui_MainWindow(Ui_MainWindown, QtWidgets.QMainWindow):
    def init2(self):
        self.li = 2
        self.spn = 0.01
        self.dot = Dot(37.620070, 55.753630)
        self.get_img()

    def get_img(self):
        params = {
            'l': l[self.li],
            'll': self.dot.__str__(),
            "spn": f"{self.spn},{self.spn}",
        }
        open('img.png', 'wb').write(requests.get(static_server, params=params).content)
        self.img.setPixmap(QtGui.QPixmap('img.png'))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_PageUp:
            if self.spn * 2 < 2:
                self.spn *= 2
        elif event.key() == Qt.Key_PageDown:
            if self.spn / 2 > 0.00175:
                self.spn /= 2
        elif event.key() == Qt.Key_Left:
            self.dot += [-self.spn * 2, 0]
        elif event.key() == Qt.Key_Right:
            self.dot += [self.spn * 2, 0]
        elif event.key() == Qt.Key_Up:
            self.dot += [0, self.spn]
        elif event.key() == Qt.Key_Down:
            self.dot += [0, -self.spn]
        self.get_img()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Ui_MainWindow()
    form.setupUi(form)
    form.init2()
    form.show()
    sys.excepthook = except_hook

    sys.exit(app.exec())
