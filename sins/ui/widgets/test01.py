# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/25/2018

from PySide.QtCore import *
from PySide.QtGui import *
import sys




if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = TestWidget2()
    panel.show()
    app.exec_()
