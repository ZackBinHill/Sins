# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/16/2018


print "# ----------------   check python modules   ---------------- #"

print "# ----------------                          ---------------- #"


import sys
from sins.module.sqt import *
from sins.ui.startup.login_ui import LoginWidget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = LoginWidget()
    panel.show()
    app.exec_()

