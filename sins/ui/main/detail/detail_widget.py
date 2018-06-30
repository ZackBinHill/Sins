# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

import sys
from sins.module.sqt import *
from sins.db.models import ModelBase
from sins.db.permission import is_editable
# from sins.config.data_view_configs import *


class DetailWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(DetailWidget, self).__init__(*args, **kwargs)

        self.instance = None
        self.model = None
        self.config = None
        self.in_fields = []
        self.view_field_names = []

        self.label_text_color = 'rgb(10, 10, 10, 100)'

        self.masterLayout = QFormLayout()
        self.setLayout(self.masterLayout)

    def init_ui(self):
        for field in self.in_fields:
            if field.name != 'thumbnail' and (field.name in self.view_field_names or len(self.view_field_names) == 0):

                cellWidget = field.create_widget(treeitem=None, column=1, parent=self)

                setattr(self, '{}_cell_widget'.format(field.name), cellWidget)

                label = QLabel(field.label)
                label.setStyleSheet('color:{}'.format(self.label_text_color))
                self.masterLayout.addRow(label, cellWidget)

    def load_config(self, config):
        self.config = config
        self.set_model(self.config.db_model)
        self.in_fields = self.config.first_fields

    def set_view_fields(self, field_names=[]):
        self.view_field_names = field_names

    def set_model(self, model):
        self.model = model

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






if __name__ == "__main__":
    from sins.config.data_view_configs import *
    app = QApplication(sys.argv)
    panel = DetailWidget()
    person_config = PersonConfig()
    panel.load_config(person_config)
    # panel.set_view_fields(['last_name'])
    panel.init_ui()
    panel.set_instance(1)
    panel.show()
    app.exec_()
