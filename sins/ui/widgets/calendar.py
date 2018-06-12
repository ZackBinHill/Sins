# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 5/12/2018

import sys
from sins.module.sqt import *
from sins.module.time_utils import now, datetime
from sins.utils.res import resource

TIME_CHUNKS = (
    (60 * 60 * 24 * 365, 'year'),
    (60 * 60 * 24 * 30, 'month'),
    (60 * 60 * 24, 'day'),
    (60 * 60, 'hour'),
    (60, 'minute'),
    (1, 'second'),
)


def get_detail_time_delta(time_delta):
    result = []
    for seconds, unit in TIME_CHUNKS:
        count = time_delta // seconds
        time_delta -= count * seconds
        result.append([count, unit])
    return result


class Calendar(QCalendarWidget):
    def __init__(self, parent=None):
        super(Calendar, self).__init__(parent)

        self.setWindowFlags(Qt.Popup)

        self.setMaximumHeight(220)

        style_text = resource.get_style("calendar")
        self.setStyleSheet(style_text)


class ClockWidget(QWidget):
    def __init__(self):
        super(ClockWidget, self).__init__()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.hourHand = [QPoint(0, 0), QPoint(0, -40)]
        self.minuteHand = [QPoint(0, 0), QPoint(0, -70)]
        self.hourColor = QColor(127, 0, 127)
        self.minuteColor = QColor(0, 127, 127)
        self.hourPen = QPen(self.hourColor)
        self.hourPen.setWidth(5)
        self.minPen = QPen(self.minuteColor)
        self.minPen.setWidth(3)

        self.time = now()

    def set_time(self, time):
        self.time = time
        self.update()

    def paintEvent(self, QPaintEvent):

        side = min(self.width(), self.height())

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setPen(self.minPen)
        painter.save()
        painter.rotate(6.0 * (self.time.minute + self.time.second / 60))
        painter.drawLine(self.minuteHand[0], self.minuteHand[1])
        painter.restore()

        painter.setPen(self.hourPen)
        painter.save()
        painter.rotate(30.0 * (self.time.hour + self.time.minute / 60))
        painter.drawLine(self.hourHand[0], self.hourHand[1])
        painter.restore()

        painter.setPen(self.hourColor)
        for i in range(12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        painter.setPen(self.minuteColor)
        for i in range(60):
            if i % 5 != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        painter.end()


class ClockWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(ClockWindow, self).__init__(*args, **kwargs)

        self.time = now()

        self.clockWidget = ClockWidget()
        self.hourEdit = QSpinBox()
        self.hourEdit.setRange(0, 23)
        self.minEdit = QSpinBox()
        self.minEdit.setRange(0, 59)

        self.masterLayout = QVBoxLayout()
        self.editlayout = QFormLayout()
        self.editlayout.addRow('Hour:', self.hourEdit)
        self.editlayout.addRow('Minute:', self.minEdit)
        self.masterLayout.addWidget(self.clockWidget)
        self.masterLayout.addLayout(self.editlayout)
        self.setLayout(self.masterLayout)

        self.hourEdit.valueChanged.connect(self.time_changed)
        self.minEdit.valueChanged.connect(self.time_changed)

        style_text = resource.get_style("calendar")
        self.setStyleSheet(style_text)

        self.set_time(self.time)

    def time_changed(self):
        self.time = datetime.time(hour=self.hourEdit.value(), minute=self.minEdit.value())
        self.clockWidget.set_time(self.time)

    def set_time(self, time):
        self.time = time
        self.clockWidget.set_time(time)
        self.hourEdit.setValue(time.hour)
        self.minEdit.setValue(time.minute)


class CalendarClock(QWidget):
    chooseTime = Signal()

    def __init__(self, *args, **kwargs):
        super(CalendarClock, self).__init__(*args, **kwargs)

        self.setWindowFlags(Qt.Popup)

        self.time = now()

        self.calendar = Calendar()
        self.clock = ClockWindow()
        self.applyButton = QPushButton('Apply')
        self.cancelButton = QPushButton('Cancel')

        self.masterLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignRight)
        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.masterLayout.addWidget(self.calendar)
        self.masterLayout.addWidget(self.clock)
        self.masterLayout.addLayout(self.buttonLayout)
        self.setLayout(self.masterLayout)

        self.applyButton.clicked.connect(self.apply_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)

        self.setStyleSheet("""
        QPushButton{
            border:none;
            background:rgb(150, 190, 220);
            width:50px;
            height:30px;
        }
        QPushButton:hover{
            background:rgb(160, 180, 230);
        }
        QPushButton:pressed{
            background:rgb(130, 150, 200);
        }
        """)

        self.resize(360, 520)

    def set_time(self, time):
        self.time = time
        self.clock.set_time(time)
        self.calendar.setSelectedDate(QDate(time.year, time.month, time.day))

    def apply_clicked(self):
        date = self.calendar.selectedDate().toPyDate()
        self.time = datetime.datetime(year=date.year,
                                      month=date.month,
                                      day=date.day,
                                      hour=self.clock.hourEdit.value(),
                                      minute=self.clock.minEdit.value())
        self.chooseTime.emit()
        self.close()

    def cancel_clicked(self):
        self.close()


class TimedeltaWidget(QWidget):
    editFinish = Signal()

    def __init__(self, *args, **kwargs):
        super(TimedeltaWidget, self).__init__(*args, **kwargs)

        self.setWindowFlags(Qt.Popup)

        self.yearEdit = QSpinBox()
        self.monthEdit = QSpinBox()
        self.dayEdit = QSpinBox()
        self.hourEdit = QSpinBox()
        self.minuteEdit = QSpinBox()
        self.secondEdit = QSpinBox()

        self.formLayout = QFormLayout()
        self.formLayout.addRow('Year:', self.yearEdit)
        self.formLayout.addRow('Month:', self.monthEdit)
        self.formLayout.addRow('Day:', self.dayEdit)

        self.layout2 = QHBoxLayout()
        self.layout2.addWidget(self.hourEdit)
        self.layout2.addWidget(QLabel(':'))
        self.layout2.addWidget(self.minuteEdit)
        self.layout2.addWidget(QLabel(':'))
        self.layout2.addWidget(self.secondEdit)

        self.masterLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.formLayout)
        self.masterLayout.addLayout(self.layout2)
        self.setLayout(self.masterLayout)

        style_text = resource.get_style("calendar")
        self.setStyleSheet(style_text)

        self.resize(300, 160)

    def set_time(self, time_delta):
        # print time_delta
        if isinstance(time_delta, datetime.datetime):
            self.yearEdit.setValue(time_delta.year)
            self.monthEdit.setValue(time_delta.month)
            self.dayEdit.setValue(time_delta.day)
            self.hourEdit.setValue(time_delta.hour)
            self.minuteEdit.setValue(time_delta.minute)
            self.secondEdit.setValue(time_delta.second)
        if isinstance(time_delta, int):
            result = get_detail_time_delta(time_delta)
            self.yearEdit.setValue(result[0][0])
            self.monthEdit.setValue(result[1][0])
            self.dayEdit.setValue(result[2][0])
            self.hourEdit.setValue(result[3][0])
            self.minuteEdit.setValue(result[4][0])
            self.secondEdit.setValue(result[5][0])

    @property
    def time_delta(self):
        result = 0
        for index, edit in enumerate([
            self.yearEdit,
            self.monthEdit,
            self.dayEdit,
            self.hourEdit,
            self.minuteEdit,
            self.secondEdit,
        ]):
            result += edit.value() * TIME_CHUNKS[index][0]
        return result

    def closeEvent(self, *args, **kwargs):
        super(TimedeltaWidget, self).closeEvent(*args, **kwargs)
        self.editFinish.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Calendar()
    ex = ClockWindow()
    ex = CalendarClock()
    ex = TimedeltaWidget()
    ex.set_time(now())
    ex.set_time(123)
    ex.show()
    sys.exit(app.exec_())
