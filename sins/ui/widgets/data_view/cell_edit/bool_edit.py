# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import *
from .basic import CellWidget


# bool
class CellBoolEdit(CellWidget):
    def __init__(self, true_text='true', false_text='false', **kwargs):
        super(CellBoolEdit, self).__init__(**kwargs)

        self.true_text = true_text
        self.false_text = false_text

        self.statusLabel = QLabel(self)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.boolCheck = None

        self.data_value = False

        self.set_no_editable()

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            self.statusLabel.setText(self.true_text if value else self.false_text)

    def set_editable(self):
        if self.boolCheck is None:
            self.boolCheck = QCheckBox(self)
            self.boolCheck.clicked.connect(self.edit_finished)
        self.statusLabel.setVisible(False)
        self.boolCheck.setVisible(True)
        self.boolCheck.setChecked(self.data_value)

    def set_no_editable(self):
        if self.boolCheck is not None:
            self.data_value = self.boolCheck.isChecked()
            self.boolCheck.setVisible(False)
        self.statusLabel.setText(self.true_text if self.data_value else self.false_text)
        self.statusLabel.setVisible(True)

    def resizeEvent(self, *args, **kwargs):
        super(CellBoolEdit, self).resizeEvent(*args, **kwargs)
        self.statusLabel.setFixedWidth(self.width())

