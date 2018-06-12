# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/6/2018

from sins.module.sqt import *
from sins.utils.res import resource


class QLabelButton(QLabel):
    buttonClicked = Signal()

    def __init__(self, name, colorDict={}, scale=24):
        super(QLabelButton, self).__init__()

        self.normalbackcolor = colorDict["normalbackcolor"]
        self.hoverbackcolor = colorDict["hoverbackcolor"]
        self.clickbackcolor = colorDict["clickbackcolor"]

        self.normalcolor = colorDict["normalcolor"]
        self.hovercolor = colorDict["hovercolor"]
        self.clickcolor = colorDict["clickcolor"]

        if name.find("/") != -1:
            self.normalpixmap = resource.get_pixmap("%s_%s.png" % (name, self.normalcolor), scale=scale)
            self.hiverpixmap = resource.get_pixmap("%s_%s.png" % (name, self.hovercolor), scale=scale)
            self.clickpixmap = resource.get_pixmap("%s_%s.png" % (name, self.clickcolor), scale=scale)
        else:
            self.normalpixmap = resource.get_pixmap("button", "%s_%s.png" % (name, self.normalcolor), scale=scale)
            self.hiverpixmap = resource.get_pixmap("button", "%s_%s.png" % (name, self.hovercolor), scale=scale)
            self.clickpixmap = resource.get_pixmap("button", "%s_%s.png" % (name, self.clickcolor), scale=scale)

        # self.setToolTip(name)
        self.setPixmap(self.normalpixmap)
        self.setStyleSheet("background-color: %s" % self.normalbackcolor)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(scale, scale)


    def enterEvent(self, event):
        self.setPixmap(self.hiverpixmap)
        self.setStyleSheet("background-color: %s" % self.hoverbackcolor)

    def leaveEvent(self, event):
        self.setPixmap(self.normalpixmap)
        self.setStyleSheet("background-color: %s" % self.normalbackcolor)

    def mousePressEvent(self, event):
        self.setPixmap(self.clickpixmap)
        self.setStyleSheet("background-color: %s" % self.clickbackcolor)

    def mouseReleaseEvent(self, event):
        self.buttonClicked.emit()
        self.setPixmap(self.hiverpixmap)
        self.setStyleSheet("background-color: %s" % self.hoverbackcolor)
