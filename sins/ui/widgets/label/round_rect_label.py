# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/21/2018

from sins.module.sqt import *
from sins.test.test_res import TestPic
import sys


class RoundRectLabel(QLabel):
    def __init__(self, round=None, *args, **kwargs):
        super(RoundRectLabel, self).__init__(*args, **kwargs)

        if isinstance(round, int):
            self.round_x = round
            self.round_y = round
        else:
            self.round_x = round[0]
            self.round_y = round[1]

        self.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        # super(RoundLabel, self).paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing, True)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.round_x, self.round_y)
        painter.setClipPath(path)

        pixmap = self.pixmap().scaled(self.width(),
                                      self.height(),
                                      Qt.KeepAspectRatioByExpanding,
                                      Qt.SmoothTransformation
                                      )

        if pixmap.height() > 0:
            ratio = pixmap.width() / float(pixmap.height())
            if ratio >= 1:
                painter.drawPixmap(-1 * (pixmap.width() - self.width()) / 2,
                                   (self.height() - pixmap.height()) / 2.0,
                                   pixmap)
            else:
                painter.drawPixmap((self.width() - pixmap.width()) / 2.0,
                                   -1 * (pixmap.height() - self.height()) / 2,
                                   pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = RoundRectLabel(round=20)
    panel.setPixmap(QPixmap(TestPic('user.png')))
    panel.show()
    app.exec_()
