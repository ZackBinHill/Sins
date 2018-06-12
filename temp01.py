# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import datetime

class ClockWidget(QWidget):
    def __init__(self):
        super(ClockWidget, self).__init__()

        self.hourHand = [QPoint(0, 0), QPoint(0, -40)]
        self.minuteHand = [QPoint(0, 0), QPoint(0, -70)]
        self.hourColor = QColor(127, 0, 127)
        self.minuteColor = QColor(0, 127, 127)
        self.hourPen = QPen(self.hourColor)
        self.hourPen.setWidth(5)
        self.minPen = QPen(self.minuteColor)
        self.minPen.setWidth(3)

        self.time = datetime.datetime.now()

    def set_time(self, time):
        self.time =  time
        self.update()

    def paintEvent(self, QPaintEvent):

        side = min(self.width(), self.height())
        time = QTime.currentTime()

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setPen(self.hourPen)
        painter.save()
        painter.rotate(30.0 * (self.time.hour + self.time.minute / 60))
        painter.drawLine(self.hourHand[0], self.hourHand[1])
        painter.restore()

        painter.setPen(self.minPen)
        painter.save()
        painter.rotate(6.0 * (self.time.minute + self.time.second / 60))
        painter.drawLine(self.minuteHand[0], self.minuteHand[1])
        painter.restore()

        painter.setPen(self.hourColor)
        for i in range(12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        painter.setPen(self.minuteColor)
        for i in range(60):
            if i % 5 != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        painter.end()

app = QApplication(sys.argv)
clock = ClockWidget()
clock.show()
app.exec_()