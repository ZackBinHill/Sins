# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/16/2018

import os

if os.getenv("QT_PREFERRED_BINDING") is None:
    os.environ['QT_PREFERRED_BINDING'] = 'PyQt4'
    # os.environ['QT_PREFERRED_BINDING'] = 'PyQt5'
    # os.environ['QT_PREFERRED_BINDING'] = 'PySide'
    # os.environ['QT_PREFERRED_BINDING'] = 'PySide2'

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *
# from Qt.QtSvg import *
from Qt import QtCompat, QtSvg, __binding__

print('using qt binding: {}'.format(__binding__))

use_qtcharts = False
if __binding__ == 'PyQt5':
    try:
        import PyQt5.QtChart as QtCharts
        use_qtcharts = True
    except:
        pass
elif __binding__ == 'PySide2':
    try:
        from PySide2 import QtCharts
        use_qtcharts = True
    except:
        pass


def loadUI(uifile, parent):
    QtCompat.loadUi(uifile=uifile, baseinstance=parent)


# for pycharm auto complete
if False:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import QtSvg, QtCharts

