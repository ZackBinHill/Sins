# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/25/2018

from PySide.QtCore import *
from PySide.QtGui import *
import sys


class LinkObject(QObject):
    link = Signal(str)
    link_objects = list()
    def add_link_object(self, object):
        self.link_objects = []
        self.link_objects.append(object)
    def create_signal(self):
        print self.__class__, 'create link'
        print self.link_objects
        for obj in self.link_objects:
            obj.link.connect(self.emit_link)
    def emit_link(self, link_str):
        self.link.emit(link_str)


class LinkLabel(QLabel):
    link = Signal(str)
    def __init__(self, text, parent=None):
        super(LinkLabel, self).__init__(text, parent)

        self.url = 'test url'

    def mouseReleaseEvent(self, *args, **kwargs):
        super(LinkLabel, self).mouseReleaseEvent(*args, **kwargs)
        self.link.emit(self.url)


class TestWidget1(QWidget, LinkObject):
    def __init__(self, parent=None):
        super(TestWidget1, self).__init__(parent)

        label = LinkLabel("aaa", self)
        # self.link_objects = []
        # self.link_objects.append(label)
        self.add_link_object(label)

        self.create_signal()

    def create_signal(self):
        super(TestWidget1, self).create_signal()
        print 'other signal'


class TestWidget2(QWidget, LinkObject):
    def __init__(self, parent=None):
        super(TestWidget2, self).__init__(parent)

        widget1 = TestWidget1(self)
        # self.link_objects = []
        # self.link_objects.append(widget1)
        self.add_link_object(widget1)
        widget1.link.connect(self.open_new)

        self.create_signal()

    def open_new(self, url):
        print 'open:', url



if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = TestWidget2()
    panel.show()
    app.exec_()
