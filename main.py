'''
при проверке pgup/pgdn проверьте что не изменяете текст или комбобокс
'''

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
    def __init__(self, *args):
        if args[0].__class__.__name__ == 'float':
            self.a, self.b = args[:2]
        else:
            self.a, self.b = map(float, args[0].split())

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

    def pt(self):
        return f'{self.a},{self.b},pmwts'

    def __repr__(self):
        return f'{self.a} {self.b}'

    def __copy__(self):
        return Dot(self.__repr__())


class Ui_MainWindow(Ui_MainWindown, QtWidgets.QMainWindow):
    def init2(self):
        self.comboBox.addItems(l)
        self.li = 2
        self.dots = []
        self.spn = 0.01
        self.maindot = Dot(55.0, 54.0)
        self.get_img()
        self.pushButton.clicked.connect(self.get_img)
        self.pushButton_find.clicked.connect(self.find_pos)
        self.pushButton_clear.clicked.connect(self.clear_dots)
        self.checkBox.clicked.connect(self.find_pos)

    def clear_dots(self):
        self.dots.clear()
        self.adres.setText('')
        self.get_img()

    def find_pos(self):
        if self.textEdit.toPlainText():
            params = {
                'apikey': geocode_key,
                "geocode": self.textEdit.toPlainText() if self.textEdit.toPlainText() else self.dots[0].__str__(),
                "format": "json"
            }
            response = \
                requests.get(geocode_server, params=params).json()['response']['GeoObjectCollection']['featureMember'][
                    0]

            self.maindot = Dot(
                response['GeoObject']['Point']['pos'])
            self.dots.append(self.maindot.__copy__())
        self.adres.setText('')
        self.textEdit.setText('')

        for dot in self.dots:
            params = {
                'apikey': geocode_key,
                "geocode": dot.__str__(),
                "format": "json"
            }
            response = \
                requests.get(geocode_server, params=params).json()['response']['GeoObjectCollection']['featureMember'][
                    0]
            self.adres.setText(
                self.adres.toPlainText() + '\n' + '-' * 8 + "\n" +
                response['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address'][
                    'formatted'] + '\n' +
                response['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address'][
                    'postal_code'] if self.checkBox.isChecked() and 'postal_code' in
                                      response['GeoObject']['metaDataProperty']['GeocoderMetaData'][
                                          'Address'] else
                self.adres.toPlainText() + "\n" + '-' * 8 + "\n" +
                response['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address'][
                    'formatted'])
            self.get_img()

    # def mousePressEvent(self, event):
    #     if (event.button() == Qt.LeftButton):
    #         pos = (event.x(), event.y())
    #         if 0<=event[0]-10<=600 and 0<=pos[1]-10<=450:


    def get_img(self):
        params = {
            'l': self.comboBox.currentText(),
            'll': self.maindot.__str__(),
            "spn": f"{self.spn},{self.spn}",
            'pt': '~'.join(map(lambda x: x.pt(), self.dots))
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
            self.maindot += [-self.spn * 2, 0]
        elif event.key() == Qt.Key_Right:
            self.maindot += [self.spn * 2, 0]
        elif event.key() == Qt.Key_Up:
            self.maindot += [0, self.spn]
        elif event.key() == Qt.Key_Down:
            self.maindot += [0, -self.spn]
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
