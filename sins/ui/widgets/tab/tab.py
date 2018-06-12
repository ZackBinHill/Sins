# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/12/2018

import sys
from sins.module.sqt import *

class TabWidget(QTabWidget):
    def __init__(self):
        super(TabWidget, self).__init__()

        self.setTabBar(TabBar())

        self.tabBar().selectedTabIndex.connect(self.update_tab)

    def update_tab(self, index):
        # print index
        widget = self.widget(index)
        if hasattr(self.widget(index), "update_data"):
            widget.update_data()
        else:
            print self.widget(index), "model_attr 'update_data' not exist"
            pass


class TabBar(QTabBar):
    selectedTabIndex = Signal(int)
    def __init__(self):
        super(TabBar, self).__init__()

    def enterEvent(self, *args, **kwargs):
        super(TabBar, self).enterEvent(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, QMouseEvent):
        super(TabBar, self).mousePressEvent(QMouseEvent)
        # print self.currentIndex()
        self.selectedTabIndex.emit(self.currentIndex())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = TabWidget()
    panel.addTab(QLabel("aaa"), "aaa")
    panel.addTab(QLabel("bbb"), "bbb")
    panel.show()
    app.exec_()