# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *
import sys

class TextBrowser(QTextBrowser):
    def __init__(self):
        super(TextBrowser, self).__init__()

        self.setOpenLinks(False)

    def loadResource(self, type, name):
        # super(TextBrowser, self).loadResource(type, name)
        # print type, name
        return


class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()

        self.label = QLabel(self)
        self.label.setStyleSheet('background:gray')
        self.label.setWordWrap(True)
        self.label.setScaledContents(True)
        self.label.setText(u'<a href="aaa.com">aaa\ndfvaa</a>sesad测试测\n试测试测\n试测试测试测试测试测试rgf adrgsdf vzdafv sadff sadfgvasq1')


    def resizeEvent(self, *args, **kwargs):
        super(Widget, self).resizeEvent(*args, **kwargs)
        self.label.setFixedWidth(self.width())





if __name__ == "__main__":
    app = QApplication(sys.argv)
    # panel = TextBrowser()
    panel = Widget()
    panel.show()
    app.exec_()

