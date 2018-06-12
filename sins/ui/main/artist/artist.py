# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/11/2018

import sys
# sys.path.append('../')
from sins.module.sqt import *
from sins.ui.widgets.tab.tab import TabWidget
from sins.ui.widgets.tab.custom_tab import CustomTabWindow, CustomTabButton
from sins.ui.widgets.tab.property_widget import PropertyWidget
from sins.utils.res import resource


class ArtistTabButton(CustomTabButton):
    def __init__(self, text, icon=None, pulldown=None, menu=None, hide=False, parent=None):
        colorDict = {
            "color":"black",
            'background':"transparent",
            "hovercolor":"gray",
            "hoverbackground":"transparent",
            "selectedcolor":"rgb(150, 150, 250)",
            "selectedbackground":"transparent",
        }
        super(ArtistTabButton, self).__init__(text, colorDict, icon, pulldown, menu, height=35, marginSize=15, hide=hide, parent=parent)


class ArtistMainWindow(CustomTabWindow, PropertyWidget):
    def __init__(self):
        super(ArtistMainWindow, self).__init__()

        self.init_ui()

    def init_ui(self):

        self.add_tab(QLabel("My Task"), ArtistTabButton("My Task"), "My Task")
        self.add_tab(QLabel("My Note"), ArtistTabButton("My Note"), "My Note")
        self.add_tab(QLabel("Personal Info"), ArtistTabButton("Personal Info"), "Personal Info")

        self.load_tab(align=Qt.AlignRight)

        self.tabWidget.tabBar().setObjectName("ArtistMainWindow_TabBar")
        self.tabWidget.setObjectName("ArtistMainWindow")

        self.set_back_color("white")

        styleText = resource.get_style("artist")
        self.setStyleSheet(styleText)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = ArtistMainWindow()
    panel.show()
    app.exec_()