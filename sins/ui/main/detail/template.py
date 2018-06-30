# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

import sys
from sins.module.sqt import *
from sins.db.permission import is_editable
from sins.ui.widgets.label import ThumbnailLabel
from sins.ui.widgets.tab.tab import TabWidget
from sins.ui.widgets.tab.custom_tab import CustomTabWindow, DefaultTabButton
from sins.ui.widgets.tab.property_widget import PropertyWidget
from sins.ui.widgets.data_view.data_table import DataWidget
from sins.ui.main.detail.detail_widget import DetailWidget
from sins.db.models import *


logger = get_logger(__name__)


THUMBNAIL_SIZE = [220, 220 *9.0 / 16]


class DetailTemplate(QSplitter):
    def __init__(self, *args, **kwargs):
        super(DetailTemplate, self).__init__(*args, **kwargs)

        self.config = None
        self.tabs = []

        self.label_text_color = 'rgb(10, 10, 10, 100)'

    def init_ui(self):
        info_layout = QHBoxLayout()
        info_layout1 = QFormLayout()
        info_layout2 = QFormLayout()

        thumbnail_field = self.config.find_field('thumbnail')
        if thumbnail_field is not None:
            thumbnail_label = thumbnail_field.create_widget(treeitem=None, column=1, parent=self)
            thumbnail_label.auto_resize = False
            thumbnail_label.setFixedSize(THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1])
            info_layout.addWidget(thumbnail_label)

        for field_name in self.view_field_names1[:4]:
            field = self.config.find_field(field_name)
            cellWidget = field.create_widget(treeitem=None, column=1, parent=self)

            setattr(self, '{}_cell_widget'.format(field_name), cellWidget)

            label = QLabel(field.label)
            label.setStyleSheet('color:{}'.format(self.label_text_color))
            info_layout1.addRow(label, cellWidget)
        info_layout.addLayout(info_layout1)

        if len(self.view_field_names1) > 4:
            for field_name in self.view_field_names1[4:]:
                field = self.config.find_field(field_name)
                cellWidget = field.create_widget(treeitem=None, column=1, parent=self)

                setattr(self, '{}_cell_widget'.format(field_name), cellWidget)

                label = QLabel(field.label)
                label.setStyleSheet('color:{}'.format(self.label_text_color))
                info_layout2.addRow(label, cellWidget)
            info_layout.addLayout(info_layout2)

        self.basic_info_widget = QWidget()
        self.basic_info_widget.setLayout(info_layout)
        self.basic_info_widget.setMaximumWidth(1000)

        self.extra_info_widget = DetailWidget()
        self.extra_info_widget.load_config(self.config)
        self.extra_info_widget.set_view_fields(self.view_field_names2)
        self.extra_info_widget.init_ui()

        info_master_layout = QVBoxLayout()
        info_master_layout.setAlignment(Qt.AlignTop)
        info_master_layout.addWidget(self.basic_info_widget)
        info_master_layout.addWidget(self.extra_info_widget)
        self.info_widget = QWidget()
        self.info_widget.setLayout(info_master_layout)

        self.info_area = QScrollArea()
        self.info_area.setWidget(self.info_widget)
        self.info_area.setWidgetResizable(True)

        self.tab_area = TabWidget()

        self.setHandleWidth(3)
        self.setOrientation(Qt.Vertical)
        self.addWidget(self.info_area)

        if len(self.tabs) > 0:
            for tab in self.tabs:
                self.tab_area.addTab(tab['widget'], tab['label'])
            self.addWidget(self.tab_area)


    def load_config(self, config):
        self.config = config
        self.set_model(self.config.db_model)
        self.in_fields = self.config.in_fields
        self.set_view_field_names([self.config.basic_view_fields, self.config.extra_view_fields])

    def set_model(self, model):
        self.model = model

    def set_view_field_names(self, field_names=[]):
        """
        :param list field_names: [[], []]
        :return:
        """
        self.view_field_names = field_names
        self.view_field_names1 = field_names[0]
        self.view_field_names2 = field_names[1]

    def set_instance(self, instance):
        if isinstance(instance, ModelBase):
            self.instance = instance
        elif isinstance(instance, int):
            self.instance = self.model.get(id=instance)

        for field in self.config.first_fields:
            cell_widget_name = '{}_cell_widget'.format(field.name)
            if hasattr(self, cell_widget_name):
                cellWidget = getattr(self, cell_widget_name)
                cellWidget.set_value(getattr(self.instance, field.model_attr))
                cellWidget.set_db_instance(self.instance)
                cellWidget.set_read_only(is_editable(editable_permission=field.edit_permission,
                                                     db_instance=self.instance))

        self.extra_info_widget.set_instance(instance)

    def add_tab(self, widget=None, label=''):
        self.tabs.append({'widget': widget, 'label': label})





if __name__ == "__main__":
    from sins.config.data_view_configs import *
    app = QApplication(sys.argv)
    panel = DetailTemplate()
    person_config = PersonConfig()
    panel.load_config(person_config)
    panel.add_tab(QLabel('aa'), 'aa')
    panel.init_ui()
    panel.set_instance(2)
    panel.show()
    app.exec_()
