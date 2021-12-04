from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport


from login_signup import Ui_login_signup
from panel import Ui_Panel

import sqlite3
import re
import hashlib
import smtplib, ssl
import random
import pickle
import csv
import matplotlib.pyplot as plt
import webbrowser



try:
    with open('username_cache', 'rb') as user:
        fcache = pickle.load(user)
except:
    with open('username_cache', 'wb') as user:
        pickle.dump(None, user)

with sqlite3.connect('Acount.db') as cnx:
    cursor = cnx.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                        username TEXT NOT NULL PRIMARY KEY,
                        email TEXT, 
                        password TEXT
                    )''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS data(
                        tag INTEGER NOT NULL PRIMARY KEY, 
                        categury TEXT,
                        period TEXT,
                        amount INTEGER, 
                        description TEXT, 
                        date DATE,
                        username TEXT
            )''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS period(
                        name TEXT NOT NULL PRIMARY KEY,
                        start DATE,
                        end DATE,
                        budget INTEGER,
                        username TEXT
                        )
    ''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS category(
                        name TEXT NOT NULL PRIMARY KEY,
                        color TEXT,
                        username TEXT
                    )
    ''')
    cnx.commit()

class login_signup(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.Ui = Ui_login_signup()
        self.Ui.setupUi(self)

        # delete WindowFlag
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # connections
        self.Ui.btnchangesignup.clicked.connect(self.btnchangesignup)
        self.Ui.btnchangelogin.clicked.connect(self.btnchangelogin)
        self.Ui.btnforgopass.clicked.connect(lambda :self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_forgot))
        self.Ui.btnsignup.clicked.connect(self.signup)
        self.Ui.btnlogin.clicked.connect(self.login)
        self.Ui.btnnext.clicked.connect(self.forgot_password)
        self.Ui.btncheck_2.clicked.connect(self.enter_code)
        self.Ui.btnsub.clicked.connect(self.reset_password)

        self.show()

    def mousePressEvent(self, evt):
        """Select the toolbar."""
        self.oldPos = evt.globalPos()
    def mouseMoveEvent(self, evt):
        """Move the toolbar with mouse iteration."""
        delta = QPoint(evt.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = evt.globalPos()

    def btnchangesignup(self):
        self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_signup)
        self.Ui.stackedWidget_2.setCurrentWidget(self.Ui.page_2)

    def btnchangelogin(self):
        self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_login)
        self.Ui.stackedWidget_2.setCurrentWidget(self.Ui.page)

    def signup(self):
        """ create an acount """
        username = self.Ui.lbluser.text()
        email = self.Ui.lblemail.text()
        password = self.Ui.lblpass.text()
        confirm_password = self.Ui.lblrepeatpass.text()

        # Validation of fields
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if len(password) >= 8 and password == confirm_password:
            if re.match(regex, email):
                # Password hashing
                hash_pass = password.encode()
                hash_pass = hashlib.sha256(hash_pass)
                hash_pass = hash_pass.hexdigest()

                # inserting data into db
                try:
                    with sqlite3.connect('Acount.db') as cnx:
                        cursor = cnx.cursor()
                        cursor.execute('''INSERT INTO users VALUES(\"%s\", \"%s\", \"%s\")''' % (username, email, hash_pass))
                        cnx.commit()
                    self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_login)
                except:
                    self.Ui.label_signup_error.setText('Username is not entered or duplicate')
            else:
                self.Ui.label_signup_error.setText('invalid email')
        else:
            self.Ui.label_signup_error.setText('The password must be more than 8 digits long')

    def login(self):
        """ Login to your account """
        username = self.Ui.lblusername.text()
        password = self.Ui.lblpassword.text()
        hash_pass = password.encode()
        hash_pass = hashlib.sha256(hash_pass)
        hash_pass = hash_pass.hexdigest()

        with sqlite3.connect('Acount.db') as cnx:
            cursor = cnx.cursor()
            cursor.execute('SELECT username, password FROM users WHERE username = \'%s\' AND password = \'%s\''
                            % (username, hash_pass))
            cnx.commit()

        if cursor.fetchone() is not None:
            with open('username_cache', 'wb') as user:
                pickle.dump(username, user)
            self.panel = panel()
            self.panel.show()
            self.close()
        else:
            self.Ui.label_login_error.setText('Wrong username or password')

    def forgot_password(self):
        ''' send an email to reset password '''
        global username
        username = self.Ui.lbl_forgo_username.text()

        with sqlite3.connect('Acount.db') as cnx:
            cursor = cnx.cursor()
            cursor.execute('SELECT email FROM users WHERE username = \'%s\'' % username)

        global code
        code = random.randint(100000, 999999)
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "😁"  # Enter your address
        receiver_email = cursor.fetchone()[0]  # Enter receiver address
        password = "🤣"
        message = str(code)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

        self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_code)

    def enter_code(self):
        ''' get the code '''
        users_code = int(self.Ui.lblfcode.text())

        if users_code == code:
            self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_reset_pass)
        else:
            self.Ui.label_code_error.setText('wrong code')

    def reset_password(self):
        ''' now reset your password '''
        new_password = self.Ui.lblnewpass.text()
        new_password_confirm = self.Ui.lblnewpassre.text()

        if new_password == new_password_confirm and len(new_password) >= 8:
            hash_pass = new_password.encode()
            hash_pass = hashlib.sha256(hash_pass)
            hash_pass = hash_pass.hexdigest()

            with sqlite3.connect('Acount.db') as cnx:
                cursor = cnx.cursor()
                cursor.execute('''UPDATE users
                                SET password = \'%s\'
                                WHERE username = \'%s\';
                                ''' % (hash_pass, username))
                cnx.commit()
            self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_login)

        else:
            self.Ui.label_reset_error.setText('The password must be more than 8 digits long')


diff_style = """QPushButton{ border-radius: 20px; background-color: none; color: #fff; border: 1px solid #fff;}QPushButton:hover{ background-color: #fff; color: black;}"""
style = """QPushButton{ border-radius: 20px; background-color: #fff; color: #000; border: 1px solid #fff;}"""
class panel(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.Ui = Ui_Panel()
        self.Ui.setupUi(self)

        with open('username_cache', 'rb') as user:
            global cache
            cache = pickle.load(user)


        # delete WindowFlag
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # welcome message
        self.Ui.label_user.setText(f'Welcome {cache}')

        with sqlite3.connect('Acount.db') as cnx:
            cursor = cnx.cursor()
            cursor.execute('''SELECT name FROM period WHERE username = \'%s\' ''' % cache)
            for name in cursor:
                self.Ui.comboBox_period_insert.addItem(name[0])
                self.Ui.comboBox_period.addItem(name[0])
            
            cursor.execute('''SELECT name FROM category WHERE username = \'%s\' ''' % cache)
            for category in cursor:
                self.Ui.comboBox_category_insert.addItem(category[0])
                self.Ui.comboBox_category.addItem(category[0])

        # budget and categiry tables
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("Acount.db")
        db.open()

        period_table = QSqlQueryModel()
        period_table.setQuery(''' SELECT name, start, end, budget FROM period WHERE username = \'%s\' ''' % cache, db)

        self.Ui.tableView_budget.setModel(period_table)
        self.Ui.tableView_budget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Ui.tableView_budget.verticalHeader().setVisible(False)

        category_table = QSqlQueryModel()
        category_table.setQuery(''' SELECT name FROM category WHERE username = \'%s\' ''' % cache, db)

        self.Ui.tableView_category.setModel(category_table)
        self.Ui.tableView_category.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Ui.tableView_category.verticalHeader().setVisible(False)

        db.close()

        # ========================
        self.Ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Ui.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.show()

        # menubar connections
        self.Ui.btn_home_page.clicked.connect(self.btn_home)
        self.Ui.btn_insert_page.clicked.connect(self.btn_insert)
        self.Ui.btn_setting_page.clicked.connect(self.btn_setting)
        self.Ui.btn_about_page.clicked.connect(self.btn_about)

        # insert page connections
        self.Ui.btn_insert_budget.clicked.connect(self.insert_budget)
        self.Ui.btn_color.clicked.connect(self.category_color)
        self.Ui.btn_insert_category.clicked.connect(self.insert_category)
        self.Ui.btn_insert_amount.clicked.connect(self.insert_amount)
        

        # home page connections
        self.Ui.btn_filter.clicked.connect(self.filter)
        self.Ui.btn_refresh.clicked.connect(self.refresh)
        self.Ui.tableView_data.clicked.connect(self.show_all)
        self.Ui.btn_export_csv.clicked.connect(self.export_csv)
        self.Ui.btn_print.clicked.connect(self.handlePreview)
        self.Ui.btn_delete.clicked.connect(self.delete)
        self.Ui.btn_chart.clicked.connect(self.chart)

        # setting page connections
        self.Ui.btn_logout.clicked.connect(self.logout)
        self.Ui.btn_delete_account.clicked.connect(self.delete_acount)
        self.Ui.btn_change_username.clicked.connect(self.change)

        # about page connections
        self.Ui.btn_contact.clicked.connect(lambda: webbrowser.open('https://t.me/mani_pak'))


    def mousePressEvent(self, evt):
        """Select the toolbar."""
        self.oldPos = evt.globalPos()
    def mouseMoveEvent(self, evt):
        """Move the toolbar with mouse iteration."""
        try:
            delta = QPoint(evt.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = evt.globalPos()
        except:
            pass


    def btn_home(self):
        self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_home)
        self.Ui.btn_home_page.setStyleSheet(style)
        self.Ui.btn_insert_page.setStyleSheet(diff_style)
        self.Ui.btn_setting_page.setStyleSheet(diff_style)
        self.Ui.btn_about_page.setStyleSheet(diff_style)
    def btn_insert(self):
        self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_insert)
        self.Ui.btn_home_page.setStyleSheet(diff_style)
        self.Ui.btn_insert_page.setStyleSheet(style)
        self.Ui.btn_setting_page.setStyleSheet(diff_style)
        self.Ui.btn_about_page.setStyleSheet(diff_style)
    def btn_setting(self):
        self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_setting)
        self.Ui.btn_home_page.setStyleSheet(diff_style)
        self.Ui.btn_insert_page.setStyleSheet(diff_style)
        self.Ui.btn_setting_page.setStyleSheet(style)
        self.Ui.btn_about_page.setStyleSheet(diff_style)
    def btn_about(self):
        self.Ui.stackedWidget.setCurrentWidget(self.Ui.page_about)
        self.Ui.btn_home_page.setStyleSheet(diff_style)
        self.Ui.btn_insert_page.setStyleSheet(diff_style)
        self.Ui.btn_setting_page.setStyleSheet(diff_style)
        self.Ui.btn_about_page.setStyleSheet(style)

    def insert_budget(self):
        ''' inserting a period budget '''
        start_date = self.Ui.dateEdit_from_budget.date().toString('yyyy-MM-dd')
        end_date = self.Ui.dateEdit_to_budget.date().toString('yyyy-MM-dd')
        period_name = self.Ui.lineEdit_insert_budget_name.text()
        budget = int(self.Ui.lineEdit_insert_budget.text()) if len(self.Ui.lineEdit_insert_budget.text()) > 0 else None

        try:
            with sqlite3.connect('Acount.db') as cnx:
                cursor = cnx.cursor()
                cursor.execute('''INSERT INTO period VALUES(
                                \'%s\', \'%s\', \'%s\', \'%i\', \'%s\'
                )
                ''' % (period_name, start_date, end_date, budget, cache))
                cnx.commit()
            self.Ui.label_insert_budget_error.setText('Budget entered successfully')
            self.Ui.label_insert_budget_error.setStyleSheet('color: #2651c7;')
        except:
            self.Ui.label_insert_budget_error.setText('Name is not entered or duplicate')
            self.Ui.label_insert_budget_error.setStyleSheet('color: rgb(255, 6, 51);')

    def category_color(self):
        dialog = QColorDialog(self)
        dialog.setOption(QColorDialog.DontUseNativeDialog)
        dialog.exec_()

        global color
        color = dialog.selectedColor().name()

    def insert_category(self):
        category_name = self.Ui.lineEdit_insert_category.text()

        try:
            with sqlite3.connect('Acount.db') as cnx:
                cursor = cnx.cursor()
                cursor.execute('''INSERT INTO category VALUES(\'%s\', \'%s\', \'%s\')''' 
                                % (category_name, color, cache))
                cnx.commit()
            self.Ui.label_insert_category.setText('Entered successfully')
            self.Ui.label_insert_category.setStyleSheet('color: #2651c7;')
        except:
            self.Ui.label_insert_category.setText('Duplicate name')
            self.Ui.label_insert_category.setStyleSheet('color: rgb(255, 6, 51);')

    def insert_amount(self):
        """ daily amount """
        tag = random.randint(100000, 999999)
        period = self.Ui.comboBox_period_insert.currentText()
        amount = int(self.Ui.lineEdit_insert_amount.text()) if len(self.Ui.lineEdit_insert_amount.text()) > 0 else None 
        description = self.Ui.textEdit_description_insert.toPlainText()
        date = self.Ui.dateEdit_insert_amount.date().toString('yyyy-MM-dd')
        category = self.Ui.comboBox_category_insert.currentText()

        try:
            with sqlite3.connect('Acount.db') as cnx:
                cursor = cnx.cursor()
                cursor.execute(""" INSERT INTO data VALUES(
                    \'%i\', \'%s\', \'%s\', \'%i\', \'%s\', \'%s\', \'%s\'
                ) """ % (tag, category, period, amount, description, date, cache))
                cnx.commit()
            self.Ui.label_insert_amount_error.setText('Entered successfully')
            self.Ui.label_insert_amount_error.setStyleSheet('color: #2651c7;')
        except:
            self.Ui.label_insert_amount_error.setText('All items are required')
            self.Ui.label_insert_amount_error.setStyleSheet('color: rgb(255, 6, 51);')

    def filter(self):
        """ display main data into table and chart """

        # delete default database connection for reconnection
        QSqlDatabase.removeDatabase(QSqlDatabase.database().connectionName())

        period = self.Ui.comboBox_period.currentText()
        category = self.Ui.comboBox_category.currentText()
        
        if category == 'All':
            try:
                db1 = QSqlDatabase.addDatabase("QSQLITE")
                db1.setDatabaseName("Acount.db")
                db1.open()

                data_table = QSqlQueryModel()
                data_table.setQuery(''' 
                SELECT tag, categury, period, amount, description, date 
                FROM data 
                WHERE period = \'%s\' AND username = \'%s\'
                ''' % (period, cache), db1)

                with sqlite3.connect('Acount.db') as cnx:
                    cursor = cnx.cursor()

                    # get total amount
                    cursor.execute('''
                    SELECT SUM(amount) 
                    FROM data 
                    WHERE period = \'%s\' AND username = \'%s\'
                    ''' % (period, cache))
                    amount = cursor.fetchone()[0]

                    # get total budget
                    cursor.execute(''' 
                    SELECT budget 
                    FROM period 
                    WHERE name = \'%s\' AND username = \'%s\'
                    ''' % (period, cache))
                    budget = cursor.fetchone()[0]

                    self.Ui.tableWidget.setItem(0, 0, QTableWidgetItem(str(budget)))
                    self.Ui.tableWidget.setItem(0, 1, QTableWidgetItem(str(amount)))

                    value = amount * 100 // budget
                    if value > 100:
                        self.Ui.progressBar.setValue(100)
                        self.Ui.progressBar.setFormat(f'%p < {value}%')
                        
                    else:
                        self.Ui.progressBar.setValue(value)

                    if value >= 50 and value <= 70:
                        self.Ui.progressBar.setStyleSheet('''
                        QProgressBar::chunk{
                            border-radius: 15px;
                            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #CAC531, stop:1 #fffc00);
                        }
                        QProgressBar{
                            color: #fff;
                            border-style: none;
                            border-radius: 15px;
                            text-align: center;
                            height: 40px;
                            background-color: #ccccff;
                        }
                        ''')

                    elif value > 70:
                        self.Ui.progressBar.setStyleSheet('''
                        QProgressBar::chunk{
                            border-radius: 15px;
                            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #e52d27, stop:1 #b31217);
                        }
                        QProgressBar{
                            color: #fff;
                            border-style: none;
                            border-radius: 15px;
                            text-align: center;
                            height: 40px;
                            background-color: #ccccff;
                        }
                        ''')
            except:
                pass


        else:
            try:
                db2 = QSqlDatabase.addDatabase("QSQLITE")
                db2.setDatabaseName("Acount.db")
                db2.open()

                data_table = QSqlQueryModel()
                data_table.setQuery(''' 
                SELECT tag, categury, period, amount, description, date 
                FROM data 
                WHERE period = \'%s\' AND categury = \'%s\' AND username = \'%s\'
                ''' % (period, category, cache), db2)
                

                with sqlite3.connect('Acount.db') as cnx:
                    cursor = cnx.cursor()

                    # get total amount
                    cursor.execute('''
                    SELECT SUM(amount) 
                    FROM data 
                    WHERE period = \'%s\' AND categury = \'%s\' AND username = \'%s\'
                    ''' % (period, category, cache))
                    amount = cursor.fetchone()[0]

                    # get total budget
                    cursor.execute(''' 
                    SELECT budget 
                    FROM period 
                    WHERE name = \'%s\' AND username = \'%s\'
                    ''' % (period, cache))
                    budget = cursor.fetchone()[0]

                    self.Ui.tableWidget.setItem(0, 0, QTableWidgetItem(str(budget)))
                    self.Ui.tableWidget.setItem(0, 1, QTableWidgetItem(str(amount)))

                    value = amount * 100 // budget
                    if value > 100:
                        self.Ui.progressBar.setValue(100)
                        self.Ui.progressBar.setFormat(f'%p < {value}%')
                        
                    else:
                        self.Ui.progressBar.setValue(value)

                    if value >= 50 and value <= 70:
                        self.Ui.progressBar.setStyleSheet('''
                        QProgressBar::chunk{
                            border-radius: 15px;
                            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #CAC531, stop:1 #fffc00);
                        }
                        QProgressBar{
                            color: #fff;
                            border-style: none;
                            border-radius: 15px;
                            text-align: center;
                            height: 40px;
                            background-color: #ccccff;
                        }
                        ''')

                    elif value > 70:
                        self.Ui.progressBar.setStyleSheet('''
                        QProgressBar::chunk{
                            border-radius: 15px;
                            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #e52d27, stop:1 #b31217);
                        }
                        QProgressBar{
                            color: #fff;
                            border-style: none;
                            border-radius: 15px;
                            text-align: center;
                            height: 40px;
                            background-color: #ccccff;
                        }
                        ''')
            except:
                pass

        self.Ui.tableView_data.setModel(data_table)
        self.Ui.tableView_data.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Ui.tableView_data.setColumnHidden(0, True)
        self.Ui.tableView_data.verticalHeader().setVisible(False)

    def refresh(self):
        self.close()
        self.__init__()

    def show_all(self):
        """ show all data from table data to textedit """
        show = str(self.Ui.tableView_data.selectionModel().currentIndex().data())
        self.Ui.textEdit_description.setText(show)

    def export_csv(self):
        """ export main table data to csv file """
        path = QFileDialog.getSaveFileName(self, 'export', 'anonymous', 'CSV Files (*.csv)')
        table = self.Ui.tableView_data.model()

        if len(path[0]) != 0:
            with open(path[0], 'w', encoding='utf-8') as ex:
                writer = csv.writer(ex, lineterminator='\n')
                for row in range(table.rowCount()):
                    rowdata = []
                    for column in range(table.columnCount()):
                        index = table.index(row, column)

                        item = str(table.data(index))
                        rowdata.append(item) 

                    writer.writerow(rowdata)
        else:
            pass


    def handlePreview(self):
        dialog = QtPrintSupport.QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()
    def handlePaintRequest(self, printer):
        try:
            document = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(document)
            model = self.Ui.tableView_data.model()
            table = cursor.insertTable(
                model.rowCount(), model.columnCount())
            for row in range(table.rows()):
                for column in range(table.columns()):
                    index = model.index(row, column)
                    cursor.insertText(str(model.data(index)))
                    cursor.movePosition(QtGui.QTextCursor.NextCell)
            document.print_(printer)
        except:
            pass

    def delete(self):
        """ delete selected row from tables """
        try:
            if self.Ui.radioButton_3.isChecked():
                row = self.Ui.tableView_data.selectionModel().currentIndex().row()
                index = self.Ui.tableView_data.model().index(row, 0)
                tag = self.Ui.tableView_data.model().data(index)

                with sqlite3.connect('Acount.db') as cnx:
                    cursor = cnx.cursor()
                    cursor.execute('''
                    DELETE FROM data WHERE tag = \'%i\' AND username = \'%s\'
                    ''' % (tag, cache))
                    cnx.commit()

            elif self.Ui.radioButton_2.isChecked():
                row = self.Ui.tableView_category.selectionModel().currentIndex().row()
                index = self.Ui.tableView_category.model().index(row, 0)
                name = self.Ui.tableView_category.model().data(index)

                with sqlite3.connect('Acount.db') as cnx:
                    cursor = cnx.cursor()
                    cursor.execute('''
                    DELETE FROM category WHERE name = \'%s\' AND username = \'%s\'
                    ''' % (name, cache))
                    cnx.commit()

            elif self.Ui.radioButton.isChecked():
                row = self.Ui.tableView_budget.selectionModel().currentIndex().row()
                index = self.Ui.tableView_budget.model().index(row, 0)
                name = self.Ui.tableView_budget.model().data(index)

                with sqlite3.connect('Acount.db') as cnx:
                    cursor = cnx.cursor()
                    cursor.execute('''
                    DELETE FROM period WHERE name = \'%s\' AND username = \'%s\'
                    ''' % (name, cache))
                    cnx.commit()
        except:
            pass

    def chart(self):
        ''' display barchart for categories '''
        period = self.Ui.comboBox_period.currentText()

        # get categories
        with sqlite3.connect('Acount.db') as cnx:
            cursor = cnx.cursor()
            cursor.execute('''
            SELECT categury
            FROM data
            WHERE period = \'%s\' AND username = \'%s\'
            ''' % (period, cache))

            categories = set(category for i in cursor.fetchall() for category in i)
            categories = list(categories)
            amount = list()
            color = list()

            # get total amount of categories
            for item in categories:
                cursor.execute('''
                SELECT SUM(amount)
                FROM data 
                WHERE categury = \'%s\' AND period = \'%s\' AND username = \'%s\'
                '''% (item, period, cache))
                amount.append(cursor.fetchone()[0])

                # get categories color code
                cursor.execute('''
                SELECT color
                FROM category 
                WHERE name = \'%s\' AND username = \'%s\'
                '''% (item, cache))
                color.append(cursor.fetchone()[0])

            # get budget of period
            cursor.execute('''
            SELECT budget
            FROM period 
            WHERE name = \'%s\' AND username = \'%s\'
            '''% (period, cache))
            budget = cursor.fetchone()[0]

        # displaying chart
        count = budget // 10
        
        fig, (ax1, ax2) = plt.subplots(2, figsize=(12, 7))


        ax1.bar(categories, amount, color=color)
        ax2.pie(amount, labels=categories, colors=color, shadow=True, autopct='%.2f')
        ax1.set_yticks(range(0, budget + 1, count))
        ax1.set_ylabel('total budget')
        ax1.set_xlabel('all categories')
        fig.tight_layout()
        plt.show()

    def logout(self):
        with open('username_cache', 'wb') as user:
            pickle.dump(None, user)
        register = login_signup()
        register.show()
        self.close()

    def delete_acount(self):
        if self.Ui.checkBox_sure.isChecked():
            with sqlite3.connect('Acount.db') as cnx:
                cursor = cnx.cursor()
                cursor.execute('''
                DELETE FROM data WHERE username = \'%s\'
                ''' % cache)
                cursor.execute('''
                DELETE FROM users WHERE username = \'%s\'
                ''' % cache)
                cursor.execute('''
                DELETE FROM period WHERE username = \'%s\'
                ''' % cache)
                cursor.execute('''
                DELETE FROM category WHERE username = \'%s\'
                ''' % cache)

            with open('username_cache', 'wb') as user:
                pickle.dump(None, user)

            register = login_signup()
            register.show()
            self.close()
        else:
            self.Ui.label_account_setting_error.setText('Please confirm')
            self.Ui.label_account_setting_error.setStyleSheet('color: rgb(255, 6, 51);')

    def change(self):
        uername_change = self.Ui.lineEdit_change_username.text()

        try:
            with sqlite3.connect('Acount.db') as cnx:
                cursor = cnx.cursor()
                cursor.execute('''
                UPDATE users
                SET username = \'%s\'
                WHERE username = \'%s\'
                '''% (uername_change, cache))
                cursor.execute('''
                UPDATE category
                SET username = \'%s\'
                WHERE username = \'%s\'
                '''% (uername_change, cache))
                cursor.execute('''
                UPDATE data
                SET username = \'%s\'
                WHERE username = \'%s\'
                '''% (uername_change, cache))
                cursor.execute('''
                UPDATE period
                SET username = \'%s\'
                WHERE username = \'%s\'
                '''% (uername_change, cache))

                cnx.commit()

            with open('username_cache', 'wb') as user:
                pickle.dump(uername_change, user)

            self.refresh()
        
        except:
            self.Ui.label_account_setting_error.setText('Username is not entered or duplicate')
            self.Ui.label_account_setting_error.setStyleSheet('color: rgb(255, 6, 51);')









if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    if fcache == None:
        root = login_signup()
    else:
        root = panel()
    sys.exit(app.exec_())