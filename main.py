import datetime
import math
from io import BytesIO
from random import choice as ch

import requests
from PIL import Image

from data import db_session
from data.Orders import Orders
from data.Types import Types
from data.drons import Drons


def show_orders_db():
    session = db_session.create_session()
    orders = session.query(Orders).all()
    data = []
    for i in orders:
        summ = 0
        drones = [x.split(':') for x in i.dron_lst.split('\n')]
        for dron in drones:
            try:
                model_dron = session.query(Drons).filter(Drons.name.like("%" + dron[0] + "%")).first()
            except:
                continue
            summ += int(dron[1]) * float(model_dron.cost.replace(',', '.').
                                         replace('o', '0').
                                         replace('O', '0').
                                         replace('о', '0'))
        data.append([i.id, i.createDate, i.closeDate, i.state, summ])
    return data


def load_types():
    session = db_session.create_session()
    if session.query(Types).all() == []:
        session.add(Types(name='Аккумуляторные батареи'))
        session.add(Types(name='Прочее'))
        session.commit()


def takeParametersForTheMapScale_GEO(response):
    '''получает на вход ответ сервера http://geocode-maps.yandex.ru/1.x/ - response.
            Возвращает параметры для запроса к http://static-maps.yandex.ru/1.x/
            Возвращает словарь, ключами являются: "ll" - точка центра карты, "spn" - градусные замеры карты,
            "l" - вид карты(карта/спутник/гибридный), "pt" - метки на карте.'''
    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    uCorner = list(map(float, toponym['boundedBy']['Envelope']['upperCorner'].split()))
    lCorner = list(map(float, toponym['boundedBy']['Envelope']['lowerCorner'].split()))

    # получамем размеры объекта в градусной мере
    delta = str(uCorner[0] - lCorner[0])
    delta1 = str(uCorner[1] - lCorner[1])
    # и забиваем на них
    delta = '0.008'
    delta1 = '0.008'
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta, delta1]),
        "l": "map",
        'pt': ",".join([toponym_longitude, toponym_lattitude]) + ',pm2' + ch(['rd', 'gn', 'gr']) + 'l'
    }
    if map_params["l"] == 'map':
        delta = '0.002'
        delta1 = '0.002'
        map_params["spn"] = ",".join([delta, delta1])
    return map_params


def takeImageFromStaticMap(toponym_to_find, indx):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        print('нет запроса')
        return
    # получаем параметры для заданного объекта.
    map_params = takeParametersForTheMapScale_GEO(response)

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)
    Image.open(BytesIO(
        response.content)).save('static/img/image' + str(indx) + '.png')


# Определяем функцию, считающую расстояние между двумя точками, заданными координатами
def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


# функция нахождения координат по адресу
def find_coords(town):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + town + "&format=json"
    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
        # запишем инфу в файл. Для изучения ответов геокодера.
        file = open('test.json', 'w', encoding='utf8')
        file.write(response.text)
        file.close()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        try:
            toponym_coodrinates = tuple(map(float, toponym["Point"]["pos"].split()))
        except Exception as a:
            print(a)
            return 'Исключение по координатам'
        return toponym_coodrinates
    else:
        return 'Bad requests'


storage_coords = [('31.169596,58.564639', 'Склад 1', 'Чудестный воображаемый склад, там хранятся запрчасти'),
                  ('31.284012, 58.456071', 'Склад 2', 'Неповерете, но на этом складе работает более 3 Марсиан.'),
                  ('34.070119,60.043671', 'Склад 3, Тихий', 'Лучше не знать ничего об этом складе. Правда.')]


def fined_nearest_st(user_adress):
    global storage_coords
    distance = []
    user_coords = find_coords(user_adress)
    if user_coords == 'Исключение по координатам' and user_coords == 'Bad requests':
        return 'Неверный Адрес'
    for i in storage_coords:
        distance.append(lonlat_distance(list(map(float, i[0].split(','))), user_coords))
    return distance.index(min(distance))


from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class NearestStorageForm(FlaskForm):
    user_adress = StringField('Ваше местоположение', validators=[DataRequired()])
    submit = SubmitField('Найти ближайший склад')


class NewOrderForm(FlaskForm):
    num = IntegerField('Номер заявки', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    mail = StringField('Эл.Почта', validators=[DataRequired()])
    model = StringField('Модель дрона', validators=[DataRequired()])
    colvo = IntegerField('Количество дронов этой модели', validators=[DataRequired()])
    submit = SubmitField('Сделать заказ')


db_session.global_init('db/Tracking_drones.sqlite')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/new_order', methods=['GET', 'POST'])
def new_order_func():
    form = NewOrderForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        order = Orders()
        order.id = int(str(form.num).split('\"')[-2])
        order.createDate = str(datetime.datetime.now())
        order.closeDate = str(datetime.datetime.now())
        order.costumer = str(form.name).split('\"')[-2] + ' ' + str(form.surname).split('\"')[-2]
        dr = ['Соколиный глаз - 2000', 'Шустрик - Model S', 'Air-Cutter 2', 'Air-Cutter',
              'Соколиный глаз - 3000', 'Black wasp 2.0']
        order.dron_lst = '\n'.join([ch(dr) + ':1' for i in range(int(str(form.colvo).split('\"')[-2]))])
        order.state = 'Запрошено разрешение у ФСБ'
        session.add(order)
        session.commit()
        return redirect('/yes')
    return render_template('new_order.html', title='Сделать заказ дрона', form=form)


@app.route('/yes')
def yes_func():
    param = {}
    param['title'] = 'Заявка принята'
    return render_template('yes.html', **param)


@app.route('/nearest_storage', methods=['GET', 'POST'])
def near_st_search_func():
    form = NearestStorageForm()
    if form.validate_on_submit():
        indx = fined_nearest_st(str(form.user_adress).split('\"')[-2])
        return redirect('/storage_find/' + str(indx))
    return render_template('near_st.html', title='Найти ближайший склад', form=form)


@app.route('/storage_find/<int:number>')
def near_st_show_func(number):
    global storage_coords
    stor_ = storage_coords[number][1]
    return render_template('near_st_finded.html', title='Ближайший склад', stor=stor_, number_=number)


@app.route('/storage/<int:number>')
def st_shower_func(number):
    global storage_coords
    stor_ = storage_coords[number]
    takeImageFromStaticMap(stor_[0], number)
    return render_template('st_show.html', title='Склад' + stor_[1], stor=stor_,
                           img=url_for('static', filename='img/image' + str(number) + '.png'))


@app.route('/')
def main_func():
    param = {}
    param['title'] = 'Главная'
    return render_template('main.html', **param)


@app.route('/all_order')
def all_order_func():
    param = {}
    param['title'] = 'Все заявки на сборку'
    param['orders'] = [list(map(str, i)) for i in show_orders_db()]
    print(param['orders'])
    param['len_orders'] = len(param['orders'])
    return render_template('all_order.html', **param)


@app.route('/storages')
def storages_func():
    global storage_coords
    param = {}
    param['title'] = 'Склады'
    param['strge'] = [list(i) + [str(storage_coords.index(i))] for i in storage_coords]
    return render_template('storages.html', **param)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
