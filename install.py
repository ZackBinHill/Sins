# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/16/2018


print "# ----------------   check python modules   ---------------- #"
try:
    import numpy
except ImportError:
    print 'can\'t import numpy, ensure that you have install numpy'

print "# ----------------                          ---------------- #"
try:
    import cv2
except ImportError:
    print 'can\'t import cv2, ensure that you have install opencv for python'

print "# ----------------                          ---------------- #"
try:
    import Crypto
except ImportError:
    print 'can\'t import Crypto, ensure that you have install crypto or cryptodemo'

print "# ----------------                          ---------------- #"
try:
    import PyQt4
except ImportError:
    try:
        import PyQt5
    except ImportError:
        print 'can\'t import PyQt, ensure that you have install PyQt4 or PyQt5'

print "# ----------------                          ---------------- #"
try:
    import MySQLdb
except ImportError:
    try:
        import pymysql
    except ImportError:
        print 'can\'t import MySQLdb nor pymysql, ensure that you have install one of them'

print "# ----------------                          ---------------- #"
try:
    import peewee
except ImportError:
    print 'can\'t import peewee, download from https://github.com/coleifer/peewee'

print "# ----------------check python modules done ---------------- #"
print "# ----------------                          ---------------- #"
print "# ----------------      start install       ---------------- #"

import sys
from sins.module.sqt import *
from sins.ui.install.install_gui import InstallDialog

app = QApplication(sys.argv)
panel = InstallDialog()
panel.show()
app.exec_()


print "# ----------------                          ---------------- #"
print "# ----------------      create database     ---------------- #"
print "# ----------------     add default data     ---------------- #"
print "# ----------------      add test data       ---------------- #"







