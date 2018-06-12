# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/21/2018

import sys
import os
from sins.module.sqt import *
from sins.utils.env.consts import login_env
from sins.utils.encrypt import do_encrypt
from sins.utils.env.envop import env_set
import traceback


class LoginWidget(QWidget):
    def __init__(self):
        super(LoginWidget, self).__init__()

        self.init_ui()
        self.set_signal()

    def init_ui(self):
        loadUI('%s/login.ui' % os.path.dirname(os.path.abspath(__file__)), self)
        self.setWindowTitle('Login')
        self.loginUser.setText("root")
        self.loginPwd.setText("123456")

    def set_signal(self):
        self.loginButton.clicked.connect(self.login)
        self.rememberButton.clicked.connect(self.remember_btn_clicked)

    def login(self):
        login_user = str(self.loginUser.text())
        login_pwd = str(self.loginPwd.text())
        if login_user != '' and login_pwd != '':
            env_set(login_env.user, login_user)
            env_set(login_env.pwd, do_encrypt(login_pwd))
            try:
                import sins.db.connect_verify as test_connect
                reload(test_connect)
                test_connect.main()
                self.close()
                os.system('python %s/run_gui.py' % os.path.dirname(os.path.abspath(__file__)))
            except Exception, e:
                print e

    def remember_btn_clicked(self, clicked):
        print clicked


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = LoginWidget()
    panel.show()
    app.exec_()
