# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import *
from sins.utils.color import int10_to_rgb
from sins.ui.widgets.colorwheel import ColorWheelWindow
from sins.ui.utils.screen import get_screen_size
from .basic import CellWidget


# color
class CellColorEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellColorEdit, self).__init__(**kwargs)

        self.colorLabel = QLabel(self)
        self.colorEdit = None

        self.data_value = None

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            color = int10_to_rgb(value, max=255, alpha_index=0)
            # print color
            self.colorLabel.setStyleSheet(
                'background: rgb({}, {}, {})'.format(color[0], color[1], color[2])
            )

    def set_editable(self):
        if self.colorEdit is None:
            self.colorEdit = ColorWheelWindow()
            self.colorEdit.applyColor.connect(self.edit_finished)
        globalPos = QCursor().pos() - self.mapFromGlobal(QCursor().pos())
        screen_height = get_screen_size().height()
        if globalPos.y() + self.height() + self.colorEdit.height() < screen_height:
            self.colorEdit.move(globalPos.x(), globalPos.y() + self.height())
        else:
            self.colorEdit.move(globalPos.x(), screen_height - self.colorEdit.height())
        self.colorEdit.setVisible(True)
        # print self.data_value
        if self.data_value is not None:
            self.colorEdit.set_color(self.data_value)
        else:
            self.colorEdit.set_color(QColor(255, 255, 255, 255))

    def set_no_editable(self):
        if self.colorEdit is not None:
            value = self.colorEdit.colorWheel.color.rgba()
            self.data_value = value
            self.colorEdit.setVisible(False)
        # print self.data_value
        color = int10_to_rgb(self.data_value, max=255, alpha_index=0)
        # print color, color[0], color[1], color[2]
        self.colorLabel.setStyleSheet(
            'background: rgb({}, {}, {})'.format(color[0], color[1], color[2])
        )

    def resizeEvent(self, *args, **kwargs):
        super(CellColorEdit, self).resizeEvent(*args, **kwargs)
        self.colorLabel.setFixedSize(self.width() - 0, self.height() - 0)


