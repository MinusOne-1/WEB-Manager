import datetime
import os
import sys

import pyqtgraph as pg
import xlrd
import xlwt

if hasattr(sys, 'frosen'):
    os.environ['PATH'] = sys._MEIPASS + ';' + os.environ['PATH']
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QTableWidgetSelectionRange
from PyQt5 import QtWidgets
from data import db_session
from data.Parts import Parts
from data.Types import Types
from data.drons import Drons
from data.tech_maps import TechMaps
from data.storage import Storage
from data.Orders import Orders


def load_types():
    session = db_session.create_session()
    if session.query(Types).all() == []:
        session.add(Types(name='Аккумуляторные батареи'))
        session.add(Types(name='Прочее'))
        session.commit()


class MainMenu(QMainWindow):
    def __init__(self):
        db_session.global_init("db/Tracking_drones.sqlite")
        super().__init__()
        uic.loadUi('ui/menu.ui', self)
        self.b_loadData.clicked.connect(self.createWindow('LoadToDataBaseWindow'))
        self.b_addPart.clicked.connect(self.createWindow('AddPartWindow'))
        self.b_viewAll.clicked.connect(self.createWindow('ViewAllWindow'))
        self.b_createRequest.clicked.connect(self.createWindow('CreateOrder'))
        self.b_viewRequests.clicked.connect(self.createWindow('ViewRequestsWindow'))
        self.b_viewAKB.clicked.connect(self.createWindow('ViewAKBWindow'))
        self.b_drop_tables.clicked.connect(self.drop_tables)

    def drop_tables(self):
        self.wait_window = PopupWindow(title='Упс', text="Не работает")
        self.wait_window.show()
        # db_session.global_init("db/Tracking_drones.sqlite")
        # session = db_session.create_session()
        # for tbl in reversed(meta.sorted_tables):
        #     engine.execute(tbl.delete())
        # db_session.global_init("db/Tracking_drones.sqlite")
        # session = db_session.create_session()
        # engine = session.get_bind()
        # command = 'SET FOREIGN_KEY_CHECKS='
        # with engine.connect() as con:
        #     con.execute(command + '0')
        # # session.execute('''TRUNCATE TABLE Parts''')
        # # session.execute('''TRUNCATE TABLE TechMaps''')
        # # session.execute('''TRUNCATE TABLE Drons''')
        # # session.execute('''TRUNCATE TABLE Types''')
        # # session.execute('''TRUNCATE TABLE Storage''')
        # # session.execute('''TRUNCATE TABLE Orders''')
        # Parts.__table__.drop(engine)
        # TechMaps.__table__.drop(engine)
        # Drons.__table__.drop(engine)
        # Types.__table__.drop(engine)
        # Storage.__table__.drop(engine)
        # Orders.__table__.drop(engine)
        # with engine.connect() as con:
        #     con.execute(command + '1')
        #
        # # import sqlalchemy.ext.declarative as dec
        # # SqlAlchemyBase = dec.declarative_base()
        #
        # # SqlAlchemyBase.metadata.create_all(engine)
        # session.commit()
        # session.close()

        # db_session.global_init("db/Tracking_drones.sqlite")
        #
        # self.ok_window = Error(title='ОК', text="База данных успешно сброшена")
        # self.ok_window.show()

    def createWindow(self, name):
        def _createWindow():
            window = globals()[name]()
            setattr(self, name, window)
            getattr(self, name, window).show()

        return _createWindow


class LoadToDataBaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        load_types()
        uic.loadUi('ui/load_form.ui', self)
        self.pushButton.clicked.connect(self.viewFile)
        self.pushButton1.clicked.connect(self.viewFile)
        self.pushButton2.clicked.connect(self.viewFile)
        self.b_load.clicked.connect(self.loadFile)
        self.b_close.clicked.connect(self.close)

    def viewFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбирете файл', '')[0]
        if self.sender() == self.pushButton:
            self.e_drons.setText(fname)
        elif self.sender() == self.pushButton1:
            self.e_complact.setText(fname)
        elif self.sender() == self.pushButton2:
            self.e_cards.setText(fname)

    def loadFile(self):
        dron_file = self.e_drons.text().strip()
        complact_file = self.e_complact.text().strip()
        cards_file = self.e_cards.text().strip()
        print(os.path.exists(dron_file), os.path.exists(complact_file), os.path.exists(cards_file))
        if os.path.exists(dron_file) and os.path.exists(complact_file) and os.path.exists(cards_file):
            self.load(dron_file, complact_file, cards_file)

    def load(self, drons, complact, cards_file):
        self.wait_window = PopupWindow(title='Загрузка',
                                       text="Пожалуйста, подождите.\nИдет загрузка файлов на удаленный сервер")
        self.wait_window.show()
        wb = xlrd.open_workbook(drons)
        sh = wb.sheet_by_index(0)
        session = db_session.create_session()
        for row_number in range(1, sh.nrows):
            temp = sh.row_values(row_number)
            self.addDron(temp[1], temp[2], session)

        wb1 = xlrd.open_workbook(complact)
        sh1 = wb1.sheet_by_index(0)
        for row_number in range(1, sh1.nrows):
            temp = sh1.row_values(row_number)
            self.addParts(temp[1], temp[2], session)

        wb2 = xlrd.open_workbook(cards_file)
        sh2 = wb2.sheet_by_index(0)
        for row_number in range(1, sh2.nrows):
            temp = sh2.row_values(row_number)
            self.addTechMap(temp[1], temp[2], temp[3], session)

        session.commit()
        self.ok_window = PopupWindow(title='ОК', text="База данных успешно обновлена")
        self.ok_window.show()

    def addDron(self, name, cost, session):
        dron = Drons()
        dron.name = name
        dron.cost = cost

        session.add(dron)

    def addParts(self, name, type_, session):
        # создание элемента нужного класса
        part = Parts()
        # установка параметров элемента
        part.name = name

        part.type = session.query(Types).filter(Types.name.like("%" + type_ + "%")).first().id

        # запись элемента в базу
        session.add(part)

    def addTechMap(self, dron_name, part_name, qual, session):
        map_ = TechMaps()

        map_.id_drons = session.query(Drons).filter(Drons.name.like("%" + dron_name + "%")).first().id
        map_.id_parts = session.query(Parts).filter(Parts.name.like("%" + part_name + "%")).first().id
        map_.quantity = qual

        session.add(map_)


class CreateOrder(QMainWindow):
    def __init__(self):
        super().__init__()
        load_types()
        uic.loadUi('ui/dron_order_form.ui', self)
        self.slt_of_drons = []
        self.pushButton.clicked.connect(self.takeOrder)
        self.pushButton_2.clicked.connect(self.close)
        self.b_addDron.clicked.connect(self.addDronToOrder)

    def loadDataToTable(self, data):
        self.tableWidget.setRowCount(len(data))
        for i, elem in enumerate(data):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()

    def takeOrder(self):
        order = Orders()

        dron_lst = self.getData()
        dron_lst = '\n'.join(list(map(lambda u: ':'.join(u), dron_lst)))
        if dron_lst == '':
            win = PopupWindow(self, 'Нет указаных дронов')
            win.show()
            return
        order.dron_lst = dron_lst
        order.createDate = str(self.dateEdit.date().toPyDate())
        order.closeDate = str(self.dateEdit.date().toPyDate())
        order.costumer = self.costumer.text()
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

        win = PopupWindow(self, 'Заявка успешно создана в базе')
        win.setWindowTitle('Успешно')
        win.show()
        self.close()

    def addDronToOrder(self):
        win = AdderDronToOrder(self)
        win.show()

    def getData(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        data = []
        for row in range(rows):
            tmp = []
            for col in range(cols):
                try:
                    tmp.append(self.tableWidget.item(row, col).text())
                except AttributeError:
                    tmp.append('')
            data.append(tmp)
        return data


class AdderDronToOrder(QMainWindow):
    def __init__(self, main=None):
        super().__init__(main)
        uic.loadUi('ui/add_dron_to_order.ui', self)
        self.addDronsToComboBox()
        self.main = main
        self.pushButton.clicked.connect(self.buttons)

    def addDronsToComboBox(self):
        session = db_session.create_session()
        for i in session.query(Drons).all():
            try:
                self.dron_type.addItem(i.name)
            except AttributeError:
                print('ошибка аттрибуции')

    def buttons(self):
        numbers = self.spinBox.value()
        name = self.dron_type.currentText()
        if name == 'Дрон не выбран':
            win = PopupWindow(self, 'Дрон не выбран')
            win.show()
            return
        self.main.slt_of_drons.append([name, numbers])
        self.main.loadDataToTable(self.main.slt_of_drons)
        self.close()


class AddPartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/add_parts_form.ui', self)
        load_types()
        self.ok.clicked.connect(self.loadToDB)
        self.b_load.clicked.connect(self.loadToDB)
        self.b_close.clicked.connect(self.cclose)
        self.b_addRow.clicked.connect(self.addRow)

    def cclose(self):
        parts_lst = self.getData()
        flag = False
        for line in parts_lst:
            if any([l == '' for l in line]):
                flag = True
                self.error_window = PopupWindow()
                self.error_window.show()
        if not flag:
            self.close()

    def loadToDB(self):
        session = db_session.create_session()
        # получение данных из таблицы
        parts_lst = self.getData()

        # запись в базу данных

        for i in parts_lst:
            print(i)
            res = self.addPost(i[0], i[1], i[2])
            if not res:
                return

        self.checkOstatock(self.dateEdit.date().toPyDate(),
                           [[i.id, i.part.name, i.quantity] for i in session.query(Storage).all()])
        session.close()

        with open('log.txt', 'a+') as log:
            n = self.spinBox.value()
            date = self.dateEdit.date().toString()
            name = self.lineEdit.text()
            log.write('-----------\n')
            log.write(f'Номер: {n}     Дата: {date}\n')
            log.write(f'Ответственный: {name}\n')
            for line in parts_lst:
                s = f'Комплектующие: {line[0]} Серийный номер: {line[1]} Количество: {line[2]}'
                log.write(s + '\n')
        if self.sender() == self.ok:
            self.close()

    def getData(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        data = []
        for row in range(rows):
            tmp = []
            for col in range(cols):
                try:
                    tmp.append(self.tableWidget.item(row, col).text())
                except AttributeError:
                    tmp.append('')
            data.append(tmp)
        return data

    def addRow(self):
        rows = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rows + 1)

    def addPost(self, name, ser_num, qual):
        post = Storage()
        session = db_session.create_session()
        post.id_parts = session.query(Parts).filter(Parts.name.like("%" + name + "%")).first().id
        try:
            post.serial_number = int(ser_num)
        except Exception:
            if name.startswith('АКБ'):
                self.error_window = PopupWindow(text='Некоторые параметры не записаны')
                self.error_window.show()
                session.close()
                return False
        try:
            post.quantity = int(qual)
        except Exception:
            self.error_window = PopupWindow(text='Некоторые параметры не записаны')
            self.error_window.show()
            session.close()
            return False
        session.add(post)
        session.commit()
        return True

    def checkOstatock(self, date, lst):
        files = os.listdir('отчёты')
        print(date)
        filename = 'Остаток_на_' + str(date) + '.xls'
        if filename not in files:
            file = open('отчёты/' + filename, 'w')
            file.close()

            file = open('отчёты/otchet_lod.txt', 'r')
            dates = []
            for i in (file.read() + '\n' + str(date)).split('\n'):
                dates.append(datetime.date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2])))
            dates = '\n'.join(list(map(str, sorted(dates))))
            file.close()

            file = open('отчёты/otchet_lod.txt', 'w')
            file.write(dates)
            file.close()
            print(1)

        book = xlwt.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet("Python Sheet 1")
        sheet1.write(0, 0, '№')
        sheet1.write(0, 1, 'Комплектующее')
        sheet1.write(0, 2, 'Остаток')

        datas = lst
        print(datas)

        for row, data in enumerate(datas, start=1):
            for col, field in enumerate(data):
                sheet1.write(row, col, field)

        book.save('отчёты/' + filename)


class ViewAllWindow(QMainWindow):
    def __init__(self, inheretence=False):
        super().__init__()
        if not inheretence:
            load_types()
            uic.loadUi('ui/remainings.ui', self)
            self.b_load.clicked.connect(self.takeNote)
            self.b_print.clicked.connect(self.chooseSaveOrPrint)
            self.b_close.clicked.connect(self.close)
            self.editDateTime()

    def editDateTime(self):
        today = datetime.datetime.now().date()
        self.dateEdit.setMaximumDate(today)

    def loadDataToTable(self, data):
        self.tableWidget.setRowCount(len(data))
        for i, elem in enumerate(data):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()

    def takeNote(self, day=False, inheretence=False):
        if day is False:
            day = self.dateEdit.date().toPyDate()
        now_day = datetime.datetime.now().date()
        # Если дата в будущем вызываем ошибку
        if day > now_day:
            if not inheretence:
                warn = PopupWindow(self, 'На указаную дату нет отчёта. На предшествующие даты также нет отчётов.')
                warn.show()
            else:
                self.loadDataToTable([])
        # если дата назначено сегодня - вызываем информацию напрямую из базы
        elif day == now_day:
            self.takeDataFromBase()
        else:
            # проверка есть ли отчёт на это число
            dates_where_we_have_otchet = open('отчёты/otchet_lod.txt', 'r')
            temp = dates_where_we_have_otchet.read().split('\n')

            # если есть берём этот отч1т и выводим в таблицу
            if str(day) in temp:
                filename = 'отчёты/Остаток_на_' + str(day) + '.xls'
                self.takeDataFromFile(filename)
            else:
                temp.append(str(day))
                dates = []
                for i in temp:
                    dates.append(datetime.date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2])))
                dates = sorted(dates)
                # иначе берёмсамое близкое число, предшествующее данному и показываем отчёт за него
                indx = dates.index(day) - 1
                filename = 'отчёты/Остаток_на_' + str(dates[indx]) + '.xls'
                # Если этот индекс валидный - значит есть отчёт, который предшествует данно дате - выводим его
                if 0 <= indx:
                    self.takeDataFromFile(filename)
                else:
                    # Иначе предупреждаем об ошибке
                    if not inheretence:
                        warn = PopupWindow(self,
                                           'На указаную дату нет отчёта. На предшествующие даты также нет отчётов.')
                        warn.show()
                    else:
                        self.loadDataToTable([])

    def takeDataFromFile(self, filename):
        wb2 = xlrd.open_workbook(filename)
        sh2 = wb2.sheet_by_index(0)
        data = []
        for row_number in range(1, sh2.nrows):
            temp = sh2.row_values(row_number)
            data.append(temp)
        self.loadDataToTable(data)

    def takeDataFromBase(self):
        session = db_session.create_session()
        data = [[i.id, i.part.name, i.quantity] for i in session.query(Storage).all()]
        self.loadDataToTable(data)

    def getDataFromTable(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        data = []
        for row in range(rows):
            tmp = []
            for col in range(cols):
                try:
                    tmp.append(self.tableWidget.item(row, col).text())
                except AttributeError:
                    tmp.append('')
            data.append(tmp)
        return data

    def chooseSaveOrPrint(self):
        win = Chooser(self)
        win.show()

    def createXLSX(self):
        files = os.listdir('отчёты')
        filename = 'Остаток_на_' + str(self.dateEdit.date().toPyDate()) + '.xls'
        if filename not in files:
            file = open('отчёты/' + filename, 'w')
            file.close()

            file = open('отчёты/otchet_lod.txt', 'r')
            dates = []
            for i in (file.read() + '\n' + str(self.dateEdit.date().toPyDate())).split('\n'):
                dates.append(datetime.date(int(i.split('-')[0]), int(i.split('-')[1]), int(i.split('-')[2])))
            dates = '\n'.join(list(map(str, sorted(dates))))
            file.close()

            file = open('отчёты/otchet_lod.txt', 'w')
            file.write(dates)
            file.close()

        book = xlwt.Workbook(encoding="utf-8")
        sheet1 = book.add_sheet("Python Sheet 1")
        sheet1.write(0, 0, '№')
        sheet1.write(0, 1, 'Комплектующее')
        sheet1.write(0, 2, 'Остаток')

        datas = self.getDataFromTable()

        for row, data in enumerate(datas, start=1):
            for col, field in enumerate(data):
                sheet1.write(row, col, field)

        book.save('отчёты/' + filename)
        win = PopupWindow(self,
                          'Отчёт от остатке успешно подготовлен. Вы можете найти его по пути:\n' + os.path.abspath(
                              'отчёты/' + filename))
        win.setWindowTitle('Успешно подготовлен xls')
        win.show()

    def printingDoc(self):
        pass


class ViewAKBWindow(ViewAllWindow):
    def __init__(self):
        super().__init__(inheretence=True)
        uic.loadUi('ui/spare_parts_remaining_form.ui', self)

        self.dateEdit.dateChanged.connect(self.generate_plot)
        self.dateEdit_2.dateChanged.connect(self.generate_plot)

        self.view = view = pg.PlotWidget()
        self.curve = view.plot(name="Line")
        self.data = []
        self.generate_plot()

    def generate_dates(self):
        start_date = self.dateEdit.date().toPyDate()
        l = []
        for i in range(self.NUM_OF_DATES):
            l.append(start_date + datetime.timedelta(days=i))
        return l

    def generate_axes_dates(self):
        start_date = self.dateEdit.date().toPyDate()
        l = []
        for i in range(self.NUM_OF_DATES):
            l.append(str(start_date + datetime.timedelta(days=i))[5:])
        return l

    def generate_plot(self):
        # random_array = np.random.random_sample(20)
        self.gridLayout.removeWidget(self.view)
        self.NUM_OF_DATES = (self.dateEdit_2.date().toPyDate() -
                             self.dateEdit.date().toPyDate()).days

        self.view = view = pg.PlotWidget()
        self.curve = view.plot(name="Line")

        # # TODO: load info from db
        # import random
        # array = [random.randint(1, 100) for x in range(self.NUM_OF_DATES)]
        self.data = []
        dates = [list(zip(range(self.NUM_OF_DATES), self.generate_axes_dates()))]
        [self.takeNote(date, inheretence=True) for date in self.generate_dates()]

        xax = self.view.getAxis('bottom')
        xax.setTicks(dates)
        self.curve.setData(self.data)
        self.gridLayout.addWidget(self.view)

    def loadDataToTable(self, data: list):
        # Actually loads data to plot
        if len(data) == 0:
            self.data.append(0)
        else:
            self.data.append(sum([int(float(x[2])) for x in data]))


class PopupWindow(QtWidgets.QDialog):
    def __init__(self, main=None, text='Не все поля заполнены', title='Ошибка'):
        super().__init__(main)
        uic.loadUi('ui/error.ui', self)
        self.label.setText(text)
        self.setWindowTitle(title)


class ViewRequestsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/orders.ui', self)
        self.show_requests()
        self.tableWidget.itemSelectionChanged.connect(self.itemSelectionChanged_)
        self.pushButton.clicked.connect(self.changeState)

    def show_requests(self):
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
                    self.error_window = PopupWindow(text='Не найден дрон с именем ' + str(dron[0]))
                    self.error_window.show()
                    return
                summ += int(dron[1]) * float(model_dron.cost.replace(',', '.').
                                             replace('o', '0').
                                             replace('O', '0').
                                             replace('о', '0'))
            data.append([i.id, i.createDate, i.closeDate, i.state, summ])
        self.loadDataToTable(data)

    def loadDataToTable(self, data):
        self.tableWidget.setRowCount(len(data))
        for i, elem in enumerate(data):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()

    def itemSelectionChanged_(self):
        y = self.tableWidget.currentRow()
        self.tableWidget.setRangeSelected(QTableWidgetSelectionRange(1, y, 5, y), True)
        self.pushButton.setEnabled(True)

    def changeState(self):
        win = OrderStateChacnger(self, self.tableWidget.item(self.tableWidget.currentRow(), 3).text())
        win.show()


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


class Chooser(QMainWindow):
    def __init__(self, main=None):
        super().__init__(main)
        uic.loadUi('ui/chooser.ui', self)
        self.main = main
        self.pushButton_2.clicked.connect(self.buttons)
        self.pushButton.clicked.connect(self.buttons)

    def buttons(self):
        if self.sender() == self.pushButton_2:
            self.main.createXLSX()
        else:
            self.main.printingDoc()
        self.close()


if __name__ == 'temp':
    app = QApplication(sys.argv)
    ex = MainMenu()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    from flask import Flask, render_template

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


    @app.route('/')
    def main_func():
        param = {}
        param['title'] = 'Главная'
        return render_template('main.html', **param)


    @app.route('/new_order')
    def new_order_func():
        param = {}
        param['title'] = 'Новая Заявна на сборку'
        return render_template('new_order.html', **param)


    @app.route('/all_order')
    def all_order_func():
        param = {}
        param['title'] = 'Все заявки на сборку'
        return render_template('all_order.html', **param)


    @app.route('/storages')
    def storages_func():
        param = {}
        param['title'] = 'Склады'
        return render_template('storages.html', **param)


    app.run(port=8080, host='127.0.0.1')
