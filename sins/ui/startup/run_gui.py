# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/21/2018

import os
import sys

sys.path.insert(0, '/'.join(os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-2]))

# print sys.path
from sins.module.sqt import *
from sins.ui.main.gui import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = MainWindow()
    panel.show()
    app.exec_()
