'''
при проверке pgup/pgdn проверьте что не изменяете текст или комбобокс
'''

import sys, math

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

    def __sub__(self, other):
        print(self, other)

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
        self.z = 15
        self.maindot = Dot(55.94386499259262, 54.726269546473326)
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

    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton):
            pos = (event.x() - 10, event.y() - 10)
            if 0 <= pos[0] <= 600 and 0 <= pos[1] <= 450:
                x = pos[0] - 300
                y = -pos[1] + 225
                a, b = self.maindot.a + 360 / (2 ** self.z) * x / 256, self.maindot.b + 180 / (2 ** self.z) * y / 256
                s = Dot(a, b)
                self.dots.append(s)
                self.find_pos()
                self.dots.pop(-1)

        if (event.button() == Qt.RightButton):
            pos = (event.x() - 10, event.y() - 10)
            if 0 <= pos[0] <= 600 and 0 <= pos[1] <= 450:
                x = pos[0] - 300
                y = -pos[1] + 225
                a, b = self.maindot.a + 360 / (2 ** self.z) * x / 256, self.maindot.b + 180 / (
                                2 ** self.z) * y / 256
                s = Dot(a, b)
                self.dots.append(s)
                self.find_pos()
            # if self.lonlat_distance() <= 50:
                search_api_server = "https://search-maps.yandex.ru/v1/"
                api_key = "..."

                address_ll = str(self.maindot)

                search_params = {
                    "apikey": api_key,
                    "lang": "ru_RU",
                    "ll": address_ll,
                    "type": "biz"
                }
                geocode = str(s)
                response = requests.get(search_api_server, params=search_params)
                # Преобразуем ответ в json-объект
                json_response = response.json()

                geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

                geocoder_params = {
                    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                    "geocode": geocode,
                    "format": "json",
                }
                print(json_response)
                organization = response.json()["features"]
                # Название организации.
                org_name = organization["properties"]["CompanyMetaData"]["name"]
                # Адрес организации.
                org_address = organization["properties"]["CompanyMetaData"]["address"]

                # Получаем координаты ответа.
                point = organization["geometry"]["coordinates"]
                org_point = "{0},{1}".format(point[0], point[1])
                delta = "0.005"

                # Собираем параметры для запроса к StaticMapsAPI:
                map_params = {
                    # позиционируем карту центром на наш исходный адрес
                    "ll": address_ll,
                    "spn": ",".join([delta, delta]),
                    "l": "map",
                    # добавим точку, чтобы указать найденную аптеку
                    "pt": "{0},pm2dgl".format(org_point)
                }

                map_api_server = "http://static-maps.yandex.ru/1.x/"
                # ... и выполняем запрос
                response = requests.get(map_api_server, params=map_params)

                name = self.dots[-1]["properties"]["CompanyMetaData"]["name"]
                print(name)
                self.pt = self.maindot + ',pm2rdl'
                self.show_message(
                    msg=name,
                    style='color: white; background-color: green; '
                          'font-size: 16pt;')
                self.update_pixmap()
            else:
                print('Близкой организации не найдено')


    def lonlat_distance(self):
        """Расстояние между точками"""
        degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
        print(self.dots)
        a_lon, a_lat = self.dots[-1].a, self.dots[-1].b
        b_lon, b_lat = self.maindot.a, self.maindot.b

        # Берем среднюю по широте точку и считаем коэффициент для нее.
        radians_lattitude = math.radians((a_lat + b_lat) / 2.)
        lat_lon_factor = math.cos(radians_lattitude)

        # Вычисляем смещения в метрах по вертикали и горизонтали.
        dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
        dy = abs(a_lat - b_lat) * degree_to_meters_factor

        return round(math.sqrt(dx * dx + dy * dy), 4)


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
                self.z -= 1
        elif event.key() == Qt.Key_PageDown:
            if self.spn / 2 > 0.00175:
                self.spn /= 2
                self.z += 1
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
