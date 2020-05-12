# 9roH}$gr - пароль от архива

import datetime
import os
import sys

if hasattr(sys, 'frosen'):
    os.environ['PATH'] = sys._MEIPASS + ';' + os.environ['PATH']
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from data import db_session
from data.Types import Types
from data.drons import Drons
from data.Orders import Orders


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


def take_order_db(dron_lst, costumer):
    order = Orders()

    if dron_lst == []:
        return 'Нужно заказать хотя бы одного дрона'

    order.dron_lst = dron_lst
    order.createDate = str(datetime.datetime.now())
    order.closeDate = str(datetime.datetime.now())
    order.costumer = costumer
    order.state = 'Запрошено разрешение у ФСБ'

    session = db_session.create_session()
    temp = session.query(Orders).filter(Orders.costumer.like(order.costumer)).all()
    if temp is not None:
        test_fbi = [i.state for i in temp]
        if 'Идет сборка' in test_fbi or 'Готова к отгрузке' in test_fbi or 'Отгружена' in test_fbi:
            order.state = 'Идет сборка'

    session.add(order)
    session.commit()
    session.close()
    return 'Заявка отослана. Статус заявки: ' + order.state


class PopupWindow(QtWidgets.QDialog):
    def __init__(self, main=None, text='Не все поля заполнены', title='Ошибка'):
        super().__init__(main)
        uic.loadUi('ui/error.ui', self)
        self.label.setText(text)
        self.setWindowTitle(title)


class OrderStateChacnger(QMainWindow):
    def __init__(self, main=None, now_state='Создана'):
        super().__init__(main)
        uic.loadUi('ui/order_state_changer.ui', self)
        self.now_state = now_state
        self.addStatesToComboBox()
        self.main = main
        self.pushButton.clicked.connect(self.buttons)
        self.pushButton_2.clicked.connect(self.close)

    def addStatesToComboBox(self):
        self.lineEdit.setText(self.now_state)
        state_lst = ['Создана', 'Запрошено разрешение у ФСБ', 'Анулирована', 'Идет сборка',
                     'Готова к отгрузке', 'Отгружена']
        if self.now_state == 'Создана':
            self.combo.addItem(state_lst[1])
        if self.now_state == 'Запрошено разрешение у ФСБ':
            self.combo.addItem(state_lst[2])
            self.combo.addItem(state_lst[3])
        if self.now_state == 'Идет сборка':
            self.combo.addItem(state_lst[4])
        if self.now_state == 'Готова к отгрузке':
            self.combo.addItem(state_lst[5])

    def buttons(self):
        new_state = self.combo.currentText()
        if new_state == 'состояние не выбрано':
            win = PopupWindow(self, 'Cостояние не выбрано')
            win.show()
            return
        session = db_session.create_session()

        temp = [self.main.tableWidget.item(self.main.tableWidget.currentRow(), 0).text()
            , self.main.tableWidget.item(self.main.tableWidget.currentRow(), 1).text()
            , self.main.tableWidget.item(self.main.tableWidget.currentRow(), 2).text(),
                self.main.tableWidget.item(self.main.tableWidget.currentRow(), 3).text(),
                self.main.tableWidget.item(self.main.tableWidget.currentRow(), 4).text()]
        qer = session.query(Orders).filter(Orders.id.like(temp[0])).first()
        qer.closeDate = datetime.datetime.now().date()
        if new_state != 'Готова к отгрузке':
            qer.state = new_state
        session.commit()

        self.main.show_requests()
        self.close()


from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NearestStorageForm(FlaskForm):
    username = StringField('Наше местоположение', validators=[DataRequired()])
    submit = SubmitField('Найти ближайший склад')


db_session.global_init('db/Tracking_drones.sqlite')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@app.route('/nearest_storage', methods=['GET', 'POST'])
def near_st_func():
    form = NearestStorageForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('near_st.html', title='Авторизация', form=form)

@app.route('/storage/<number>', methods=['GET', 'POST'])
def near_st_func(number):
    form = NearestStorageForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('near_st.html', title='Авторизация', form=form)


@app.route('/')
def main_func():
    param = {}
    param['title'] = 'Главная'
    return render_template('main.html', **param)

@app.route('/all_order')
def all_order_func():
    param = {}
    param['title'] = 'Все заявки на сборку'
    param['orders'] = [list(map(str, i))for i in show_orders_db()]
    print(param['orders'])
    param['len_orders'] = len(param['orders'])
    return render_template('all_order.html', **param)



@app.route('/new_order')
def new_order_func():
    param = {}
    param['title'] = 'Новая Заявна на сборку'
    return render_template('new_order.html', **param)




@app.route('/storages')
def storages_func():
    param = {}
    param['title'] = 'Склады'
    return render_template('storages.html', **param)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
