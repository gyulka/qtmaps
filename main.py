import sys

import requests
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic
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
