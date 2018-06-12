# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/11/2018

import os
import sys
from sins.module.sqt import *
from sins.utils.res import resource
from sins.utils.surl.surl import SURL
from page import PageWindow


class MainWindow(QTabWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.init_ui()
        self.tabCloseRequested.connect(self.close_requested)
        self.addPageButton.buttonClicked.connect(self.new_page)

    def init_ui(self):

        self.setWindowTitle('Sins')

        self.add_tab()

        self.addPageButton = AddPageButton()
        self.setCornerWidget(self.addPageButton, Qt.TopRightCorner)

        self.tabBar().setObjectName("MainWindow_TabBar")
        self.setObjectName("MainWindow")

        self.setTabsClosable(True)
        self.setMovable(True)

        gui_style = resource.get_style("main_gui")
        scrollbar_style = resource.get_style("scrollbar")
        self.setStyleSheet(gui_style + scrollbar_style)

    def close_requested(self, index):
        self.close_page(index)

    def close_page(self, index):
        widget = self.widget(index)
        if self.count() == 1:
            self.close()
        self.removeTab(index)
        widget.deleteLater()

    def new_page(self):
        self.add_tab()

    def to_page(self, url):
        # print 'to page', url
        if isinstance(url, SURL):
            url = url.url
        self.add_tab(url)

    def add_tab(self, url=None):
        page = PageWindow(parent=self)
        page.logoutclicked.connect(self.logout)
        if url is None:
            page.apply_page_data('sins://page/Artist/My Task')
        else:
            page.apply_page_data(url)
        index = self.addTab(page, "aaa")
        self.setCurrentIndex(index)

    def logout(self):
        print 'log_out'
        self.close()
        cmd = 'python %s/login.py' % "/".join(os.path.abspath(__file__).split(os.sep)[:-4])
        print cmd
        os.system(cmd)


class AddPageButton(QLabel):
    buttonClicked = Signal()

    def __init__(self):
        super(AddPageButton, self).__init__()

        self.buttonWidth = 63
        self.buttonHeight = 30

        self.setToolTip("add new page")
        self.imagePixmap = resource.get_pixmap('button', 'add_page_button.png', scale=[self.buttonWidth, self.buttonHeight])
        self.imageHoverPixmap = resource.get_pixmap('button', 'add_page_button_hover.png', scale=[self.buttonWidth, self.buttonHeight])
        self.imageClickedPixmap = resource.get_pixmap('button', 'add_page_button_clicked.png', scale=[self.buttonWidth, self.buttonHeight])
        self.setPixmap(self.imagePixmap)

    def enterEvent(self, event):
        self.setPixmap(self.imageHoverPixmap)

    def leaveEvent(self, event):
        self.setPixmap(self.imagePixmap)

    def mousePressEvent(self, event):
        self.setPixmap(self.imageClickedPixmap)

    def mouseReleaseEvent(self, event):
        self.buttonClicked.emit()
        self.setPixmap(self.imageHoverPixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = MainWindow()
    panel.show()
    app.exec_()