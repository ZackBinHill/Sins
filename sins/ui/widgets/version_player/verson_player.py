# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/25/2018

import os
import sys
import time
from sins.module.sqt import *
from sins.ui.widgets.version_player.player import Player


class VersonPlayer(QWidget):
    def __init__(self):
        super(VersonPlayer, self).__init__()

        self.init_ui()

    def init_ui(self):
        self.player = Player()
        self.versonList = QTreeWidget()

        self.splitter = QSplitter()
        self.splitter.setHandleWidth(5)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.player)
        self.splitter.addWidget(self.versonList)
        # self.splitter.setStretchFactor(0, 1)
        # self.splitter.setStretchFactor(1, 3)

        self.masterLayout = QHBoxLayout()
        self.masterLayout.addWidget(self.splitter)
        self.setLayout(self.masterLayout)

        self.setStyleSheet("background:rgb(40, 40, 40)")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VersonPlayer()
    w.show()
    app.exec_()