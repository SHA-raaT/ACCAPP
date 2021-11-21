from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets


from login_signup import Ui_login_signup
from panel import Ui_Panel

import sqlite3
import re
import hashlib
import smtplib, ssl
import random
import pickle


try:
    with open('username_cache', 'rb') as user:
        cache = pickle.load(user)
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


    def mousePressEvent(self, evt):
        """Select the toolbar."""
        self.oldPos = evt.globalPos()
    def mouseMoveEvent(self, evt):
        """Move the toolbar with mouse iteration."""
        delta = QPoint(evt.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = evt.globalPos()


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
        budget = int(self.Ui.lineEdit_insert_budget.text())

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





if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    if cache == None:
        root = login_signup()
    else:
        root = panel()
    sys.exit(app.exec_())