# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import *
from sins.module.time_utils import datetime_to_str, datetime
from sins.ui.utils.screen import get_screen_size
from sins.ui.widgets.calendar import Calendar, CalendarClock, TimedeltaWidget, get_detail_time_delta
from .basic import CellWidget


# date
class CellDateEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellDateEdit, self).__init__(**kwargs)

        self.dateLabel = QLabel(self)
        self.dateLabel.move(3, 3)
        self.calendar = None
        self.dateFormat = '%Y-%m-%d'

        self.data_value = None

        # self.set_no_editable()

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            self.dateLabel.setText(datetime_to_str(value, self.dateFormat))

    def set_editable(self):
        if self.calendar is None:
            self.calendar = Calendar(self.treeitem.tree)
            self.calendar.clicked.connect(self.edit_finished)
        globalPos = QCursor().pos() - self.mapFromGlobal(QCursor().pos())
        screen_height = get_screen_size().height()
        if globalPos.y() + self.height() + self.calendar.height() < screen_height:
            self.calendar.move(globalPos.x(), globalPos.y() + self.height())
        else:
            self.calendar.move(globalPos.x(), screen_height - self.calendar.height())
        self.calendar.setVisible(True)
        if self.data_value is not None:
            self.calendar.clicked.disconnect(self.edit_finished)
            self.calendar.setSelectedDate(QDate(self.data_value.year, self.data_value.month, self.data_value.day))
            self.calendar.clicked.connect(self.edit_finished)

    def set_no_editable(self):
        if self.calendar is not None:
            self.data_value = self.calendar.selectedDate().toPyDate()
            self.calendar.setVisible(False)
        if self.data_value is not None:
            self.dateLabel.setText(datetime_to_str(self.data_value, self.dateFormat))

    def resizeEvent(self, *args, **kwargs):
        super(CellDateEdit, self).resizeEvent(*args, **kwargs)
        self.dateLabel.setFixedWidth(self.width())


class CellDateTimeEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellDateTimeEdit, self).__init__(**kwargs)

        self.dateTimeLabel = QLabel(self)
        self.dateTimeLabel.move(3, 3)
        self.calendarClock = None
        self.dateFormat = '%Y-%m-%d %H:%M'

        self.data_value = None

        # self.set_no_editable()

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            self.dateTimeLabel.setText(datetime_to_str(value, self.dateFormat))

    def set_editable(self):
        if self.calendarClock is None:
            self.calendarClock = CalendarClock(self.treeitem.tree)
            self.calendarClock.chooseTime.connect(self.edit_finished)
        globalPos = QCursor().pos() - self.mapFromGlobal(QCursor().pos())
        # print globalPos
        screen_height = get_screen_size().height()
        if globalPos.y() + self.height() + self.calendarClock.height() < screen_height:
            self.calendarClock.move(globalPos.x(), globalPos.y() + self.height())
        else:
            self.calendarClock.move(globalPos.x(), screen_height - self.calendarClock.height())
        self.calendarClock.setVisible(True)
        if self.data_value is not None:
            self.calendarClock.set_time(self.data_value)

    def set_no_editable(self):
        if self.calendarClock is not None:
            self.data_value = self.calendarClock.time
            self.calendarClock.setVisible(False)
        if self.data_value is not None:
            self.dateTimeLabel.setText(datetime_to_str(self.data_value, self.dateFormat))

    def resizeEvent(self, *args, **kwargs):
        super(CellDateTimeEdit, self).resizeEvent(*args, **kwargs)
        self.dateTimeLabel.setFixedWidth(self.width())


class CellTimedeltaEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellTimedeltaEdit, self).__init__(**kwargs)

        self.timeDeltaLabel = QLabel(self)
        self.timeDeltaLabel.move(3, 3)
        self.timeDeltaWidget = None
        self.dateFormat = '%Y-%m-%d %H:%M'

        self.data_value = None

        # self.set_no_editable()

    def update_label(self):
        if isinstance(self.data_value, datetime.datetime):
            self.timeDeltaLabel.setText(datetime_to_str(self.data_value, self.dateFormat))
        if isinstance(self.data_value, int):
            text = ''
            for index, result in enumerate(get_detail_time_delta(self.data_value)):
                if result[0] != 0:
                    text += '{}{}'.format(result[0], result[1])
            self.timeDeltaLabel.setText(text)

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            self.update_label()

    def set_editable(self):
        if self.timeDeltaWidget is None:
            self.timeDeltaWidget = TimedeltaWidget(self.treeitem.tree)
            self.timeDeltaWidget.editFinish.connect(self.edit_finished)
        globalPos = QCursor().pos() - self.mapFromGlobal(QCursor().pos())
        screen_height = get_screen_size().height()
        if globalPos.y() + self.height() + self.timeDeltaWidget.height() < screen_height:
            self.timeDeltaWidget.move(globalPos.x(), globalPos.y() + self.height())
        else:
            self.timeDeltaWidget.move(globalPos.x(), screen_height - self.timeDeltaWidget.height())
        self.timeDeltaWidget.setVisible(True)
        if self.data_value is not None:
            self.timeDeltaWidget.set_time(self.data_value)

    def set_no_editable(self):
        if self.timeDeltaWidget is not None:
            self.data_value = self.timeDeltaWidget.time_delta
            self.timeDeltaWidget.setVisible(False)
        if self.data_value is not None:
            self.update_label()

    def resizeEvent(self, *args, **kwargs):
        super(CellTimedeltaEdit, self).resizeEvent(*args, **kwargs)
        self.timeDeltaLabel.setFixedWidth(self.width())

