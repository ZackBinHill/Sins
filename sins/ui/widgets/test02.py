# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/25/2018

from PySide.QtCore import *
from PySide.QtGui import *
import sys
# from test01 import TestWidget2, LinkObject, LinkLabel

class LinkObject(QObject):
    link = Signal(str)
    link_objects = list()

    def create_signal(self):
        for obj in self.link_objects:
            obj.link.connect(self.emit_link)

    def emit_link(self, link_str):
        self.link.emit(link_str)


class LinkLabel(QLabel):
    link = Signal(str)
    def __init__(self, text, url=None, parent=None):
        super(LinkLabel, self).__init__(text, parent)

        self.url = url

    def mouseReleaseEvent(self, *args, **kwargs):
        super(LinkLabel, self).mouseReleaseEvent(*args, **kwargs)
        self.link.emit(self.url)


class LinkLabel1(QLabel):
    link = Signal(str)
    def __init__(self, text, parent=None):
        super(LinkLabel1, self).__init__(text, parent)

        self.url = 'aaaaaaa'

    def mouseReleaseEvent(self, *args, **kwargs):
        super(LinkLabel1, self).mouseReleaseEvent(*args, **kwargs)
        self.link.emit(self.url)


class TestTree1(QTreeWidget, LinkObject):
    # link = Signal(str)
    def __init__(self, parent=None):
        super(TestTree1, self).__init__(parent)

        label = LinkLabel1('aaaa', parent=self)
        self.link_objects.append(label)

        self.create_signal()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = TestTree1()
    panel.show()
    app.exec_()
