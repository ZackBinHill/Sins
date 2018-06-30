# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/9/2018

import sys
from sins.module.sqt import *
from sins.ui.widgets.tab.custom_tab import CustomTabWindow, DefaultTabButton
from sins.ui.widgets.tab.property_widget import PropertyWidget
from sins.ui.widgets.data_view.data_table import DataWidget
from sins.ui.main.detail import DetailTemplate, DetailWidget
from sins.config.data_view_configs import ShotConfig, TaskConfig
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

        self.detailWidget = DetailTemplate()
        self.detailWidget.load_config(ShotConfig())
        task_data_table = DataWidget(parent=self)
        task_data_table.load_config(config=TaskConfig())
        dailies_data_table = DataWidget(parent=self)
        publish_data_table = DataWidget(parent=self)
        note_data_table = DataWidget(parent=self)
        all_detail_widget = DetailWidget(parent=self)
        self.detailWidget.add_tab(widget=task_data_table, label='Tasks')
        self.detailWidget.init_ui()

        self.masterLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.shotChooseLayout)
        self.masterLayout.addWidget(self.detailWidget)
        self.setLayout(self.masterLayout)


class ShotAllWindow(PropertyWidget):
    def __init__(self, *args, **kwargs):
        super(ShotAllWindow, self).__init__(*args, **kwargs)

        self.coreproperty_list = ['showId']

        self.dataTable = DataWidget(parent=self)
        self.dataTable.load_config(config=ShotConfig())

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
        # self.dataTable.load_config(config=ShotConfig())
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