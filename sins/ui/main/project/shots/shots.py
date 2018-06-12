# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/9/2018

import os
import sys
from sins.module.sqt import *
from sins.ui.widgets.thumbnail_label import ThumbnailLabel
from sins.ui.widgets.tab.tab import TabWidget
from sins.ui.widgets.tab.custom_tab import CustomTabWindow, DefaultTabButton
from sins.ui.widgets.tab.property_widget import PropertyWidget
from sins.ui.widgets.table.data_table import DataWidget
from sins.ui.widgets.table.data_table_configs import ShotConfig
from sins.test.test_res import TestMov
from sins.utils.res import resource
from sins.utils.log import get_logger
from sins.db.models import *


logger = get_logger(__name__)


class ShotDetailWindow(PropertyWidget):
    def __init__(self):
        super(ShotDetailWindow, self).__init__()

        self.shotId = None

        self.coreproperty_list = ['shotId']

        self.init_ui()

    def init_ui(self):

        self.seqCombobox = QComboBox()
        self.seqCombobox.addItems(["02", "03", "04"])
        self.shotCombobox = QComboBox()
        self.shotCombobox.addItems(["0010", "0030", "0040"])
        self.goButton = QPushButton("GO")
        self.shotChooseLayout = QHBoxLayout()
        self.shotChooseLayout.addWidget(self.seqCombobox)
        self.shotChooseLayout.addWidget(self.shotCombobox)
        self.shotChooseLayout.addWidget(self.goButton)
        self.shotChooseLayout.addStretch()

        self.shotInfoWidget = ShotInfoWidget(self)
        self.shotInfoArea = QScrollArea()
        self.shotInfoArea.setWidget(self.shotInfoWidget)
        self.shotInfoArea.setWidgetResizable(True)
        self.shotTabs = ShotTabWindow()

        self.splitter = QSplitter()
        self.splitter.setHandleWidth(3)
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.addWidget(self.shotInfoArea)
        self.splitter.addWidget(self.shotTabs)
        self.masterLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.shotChooseLayout)
        self.masterLayout.addWidget(self.splitter)
        self.setLayout(self.masterLayout)

        styleText = resource.get_style("shots")
        self.setStyleSheet(styleText)


class ShotInfoWidget(QWidget):
    def __init__(self, parent=None):
        super(ShotInfoWidget, self).__init__(parent)

        self.shotPreview = ThumbnailLabel()
        self.shotPreview.create_preview(TestMov("test3.mov"))
        self.shotPreview.setFixedSize(220, 220 *9.0 / 16)
        self.layout1 = QHBoxLayout()
        self.layout12 = QVBoxLayout()
        self.label1 = QLabel("aaa")
        self.label2 = QLabel("aaa")
        self.label3 = QLabel("aaa")
        self.label4 = QLabel("aaa")
        self.layout12.addWidget(self.label1)
        self.layout12.addWidget(self.label2)
        self.layout12.addWidget(self.label3)
        self.layout12.addWidget(self.label4)
        self.layout1.addWidget(self.shotPreview)
        self.layout1.addLayout(self.layout12)

        self.shotDescription = QTextEdit()
        self.shotDescription.setPlainText("aa\naaa\naaaaaaaa\naaa\naaa\na")
        self.shotDescription.document().adjustSize()
        self.shotDescription.setFixedHeight(self.shotDescription.document().size().height())
        self.shotDescription.setReadOnly(True)


        self.masterLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.layout1)
        self.masterLayout.addWidget(self.shotDescription)
        self.masterLayout.addStretch()
        self.setLayout(self.masterLayout)

        self.setObjectName("ShotInfoWidget")


class ShotTabWindow(TabWidget):
    def __init__(self):
        super(ShotTabWindow, self).__init__()

        self.setObjectName("ShotTabWindow")
        self.tabBar().setObjectName("ShotTabWindow_TabBar")

        self.addTab(QLabel("Task"), "Task")
        self.addTab(QLabel("Dailies"), "Dailies")
        self.addTab(QLabel("Publish"), "Publish")
        self.addTab(QLabel("Note"), "Note")


class ShotAllWindow(PropertyWidget):
    def __init__(self, *args, **kwargs):
        super(ShotAllWindow, self).__init__(*args, **kwargs)

        self.coreproperty_list = ['showId']

        self.dataTable = DataWidget(parent=self)

        self.masterLayout = QVBoxLayout()
        self.masterLayout.setContentsMargins(0, 0, 0, 0)
        self.masterLayout.addWidget(self.dataTable)
        self.setLayout(self.masterLayout)

    def set_core_property(self, **kwargs):
        # print kwargs
        super(ShotAllWindow, self).set_core_property(**kwargs)
        # print self.showId
        self.dataTable.set_basic_filter([
            {'join': Project, 'where': (Project.id == self.showId)},
        ])

    def update_data(self):
        # print 'update data'
        self.dataTable.load_config(config=ShotConfig())
        self.dataTable.refresh()


class ShotMainWindow(CustomTabWindow, PropertyWidget):
    def __init__(self, *args, **kwargs):
        super(ShotMainWindow, self).__init__(*args, **kwargs)

        self.showId = None

        self.coreproperty_list = ['showId']

        self.init_ui()

        # self.create_signal()

    def init_ui(self):

        self.shotAllWindow = ShotAllWindow(parent=self)
        # self.add_link_object(self.shotAllWindow)
        self.shotDetailWindow = ShotDetailWindow()

        self.add_tab(self.shotAllWindow, DefaultTabButton("All"), "All")
        self.add_tab(self.shotDetailWindow, DefaultTabButton("Detail"), "Detail")

        self.load_tab()

        # self.customTabBar.hide()

    def set_core_property(self, **kwargs):
        super(ShotMainWindow, self).set_core_property(**kwargs)
        if self.showId is not None:
            self.shotAllWindow.set_core_property(showId=self.showId)
        # print kwargs
        # print self.showId


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = ShotMainWindow()
    panel.show()
    app.exec_()