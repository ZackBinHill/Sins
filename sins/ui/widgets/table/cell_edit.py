# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 5/23/2018

from sins.module.sqt import *
from sins.module.time_utils import current_time, today, datetime_to_str, str_to_datetime, time
from sins.utils.res import resource
from sins.utils.log import get_logger
from sins.utils.python import get_class_from_name_data
from sins.utils.color import int10_to_rgb, rgba_to_int10
from sins.ui.widgets.thumbnail_label import ThumbnailLabel
from sins.ui.widgets.calendar import Calendar, CalendarClock, TimedeltaWidget, get_detail_time_delta
from sins.ui.widgets.colorwheel import ColorWheelWindow
from sins.ui.widgets.flow_layout import FlowLayout
from sins.db.models import *
import sys
import copy
import math

logger = get_logger(__name__)

EDITLABEL_SIZE = 20
OBJECT_ICON_SIZE = 20
scrollbar_style = resource.get_style('scrollbar')


def get_screen_size():
    return QDesktopWidget().screenGeometry()


# base
class EditLabel(QLabel):
    clicked = Signal()
    def __init__(self, editable=False, parent=None):
        super(EditLabel, self).__init__(parent)
        self.editable = editable
        if self.editable:
            self.setPixmap(resource.get_pixmap("icon", "edit_darkgray.png", scale=EDITLABEL_SIZE))
        else:
            self.setPixmap(resource.get_pixmap("icon", "edit_gray.png", scale=EDITLABEL_SIZE))

        self.setFixedSize(EDITLABEL_SIZE, EDITLABEL_SIZE)

    def mouseReleaseEvent(self, *args, **kwargs):
        if self.editable:
            self.clicked.emit()


class CellWidget(QWidget):
    def __init__(self,
                 editable=False,
                 treeitem=None,
                 column=0,
                 db_instence=None,
                 model_attr='',
                 column_label='',
                 parent=None):
        super(CellWidget, self).__init__(parent)
        self.editable = editable
        self.treeitem = treeitem
        self.column = column
        self.column_label = column_label
        self.db_instence = db_instence
        self.model_attr = model_attr
        self.autoHeight = False
        self.targetHeight = 0

        self.data_value = None
        self.update_db_time = 0
        self.has_edit_label = False

        # self.setStyleSheet("border:none;background:transparent")
        self.back = QLabel(self)
        # self.back.setStyleSheet("background:rgb(100, 140, 100, 250)")

    def add_front(self, editlabel=True):
        self.has_edit_label = editlabel

    def set_value(self, value):
        pass

    def set_db_instence(self, db_instence):
        self.db_instence = db_instence

    def set_read_only(self, editable=False):
        self.editable = editable

    def set_editable(self):
        pass

    def set_no_editable(self):
        pass

    def edit_finished(self):
        self.set_no_editable()
        if current_time() - self.update_db_time > 0.01:
            # print self.db_instence, self.model_attr
            if self.db_instence is not None and (hasattr(self.db_instence, self.model_attr)):
                old_value = getattr(self.db_instence, self.model_attr)
                logger.debug(u'setattr({}, {}, {})'.format(self.db_instence, self.model_attr, self.data_value))
                setattr(self.db_instence, self.model_attr, self.data_value)
                self.db_instence.save()
                detail = u'update {column} from {old} to {new}'.format(column=self.column_label,
                                                                        old=old_value,
                                                                        new=self.data_value)
                LogTable.create(
                    table_name=self.db_instence._meta.table_name,
                    event='UPDATE',
                    event_date=datetime.datetime.now(),
                    event_data_id=self.db_instence.id,
                    event_by=current_user,
                    detail=detail,
                )
                self.update_db_time = current_time()

    def resizeEvent(self, *args, **kwargs):
        super(CellWidget, self).resizeEvent(*args, **kwargs)
        if hasattr(self, "editlabel"):
            self.editlabel.move(self.width() - EDITLABEL_SIZE, 0)
        self.back.resize(self.size())

    def enterEvent(self, QEvent):
        super(CellWidget, self).enterEvent(QEvent)
        if self.has_edit_label and not hasattr(self, "editlabel"):
            self.editlabel = EditLabel(self.editable, self)
            self.editlabel.clicked.connect(self.set_editable)
            self.editlabel.move(self.width() - EDITLABEL_SIZE, 0)
        if hasattr(self, "editlabel"):
            self.editlabel.setHidden(False)

    def leaveEvent(self, QEvent):
        super(CellWidget, self).leaveEvent(QEvent)
        if hasattr(self, "editlabel"):
            self.editlabel.setHidden(True)


# line edit
class CellLineEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellLineEdit, self).__init__(**kwargs)

        self.textLabel = QLabel('', self)
        self.textLabel.move(3, 3)
        self.lineEdit = None
        self.is_int = False
        self.is_float = False

        self.data_value = ''

        self.set_no_editable()

    def set_value(self, value):
        # print type(value)
        if value is not None:
            self.data_value = value
            if isinstance(value, (str, unicode)):
                self.textLabel.setText(value)
            elif isinstance(value, (int, long)):
                self.textLabel.setText(str(value))
                self.is_int = True
            elif isinstance(value, float):
                self.textLabel.setText(str(value))
                self.is_float = True

    def set_editable(self):
        if self.lineEdit is None:
            self.lineEdit = QLineEdit('', self)
            self.lineEdit.setStyleSheet("border:none;background:transparent")
            # self.lineEdit.editingFinished.connect(self.edit_finished)
            self.lineEdit.returnPressed.connect(self.edit_finished)
        self.lineEdit.setVisible(True)
        if self.is_int:
            self.lineEdit.setValidator(QIntValidator())
        if self.is_float:
            self.lineEdit.setValidator(QDoubleValidator())
        self.lineEdit.setText(u'{}'.format(self.data_value))
        self.textLabel.setVisible(False)
        self.lineEdit.selectAll()

    def set_no_editable(self):
        if self.lineEdit is not None:
            self.data_value = u'{}'.format(self.lineEdit.text())
            if self.is_float:
                self.data_value = float(self.data_value)
            if self.is_int:
                self.data_value = int(self.data_value)
            self.lineEdit.setVisible(False)
        self.textLabel.setVisible(True)
        # self.textLabel.setText(str(self.data_value))
        self.textLabel.setText(u'{}'.format(self.data_value))

    def resizeEvent(self, *args, **kwargs):
        super(CellLineEdit, self).resizeEvent(*args, **kwargs)
        if self.lineEdit is not None:
            self.lineEdit.setFixedWidth(self.width())
        self.textLabel.setFixedWidth(self.width())


class PasswordEdit(CellLineEdit):
    def __init__(self, **kwargs):
        super(PasswordEdit, self).__init__(**kwargs)
        self.textLabel.setText('******')
    def set_value(self, value):
        pass


# text edit
class SignalTextEdit(QTextEdit):
    editFinished = Signal()

    def __init__(self, *args, **kwargs):
        super(SignalTextEdit, self).__init__(*args, **kwargs)

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        super(SignalTextEdit, self).eventFilter(object, event)
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                # if event.key() == Qt.Key_Return:
                # print 'enter'
                self.editFinished.emit()
                return True
        return False


class CellTextEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellTextEdit, self).__init__(**kwargs)

        self.autoHeight = True

        self.data_value = ''

        # self.masterlayout = QHBoxLayout()
        # self.masterlayout.setContentsMargins(0,0,0,0)

        self.setStyleSheet("""
        *{
            border:none;
            background:transparent
        }
        """ + scrollbar_style)
        self.textLabel = QTextEdit('', self)
        self.textLabel.setReadOnly(True)
        self.textEdit = None

        # self.textLabel = QLabel('', self)
        # self.textLabel.setWordWrap(True)
        # self.textLabel.setScaledContents(True)

        self.textLabel.document().adjustSize()
        self.set_size()
        self.set_no_editable()

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            self.textLabel.setText(value)

    def set_editable(self):
        if self.textEdit is None:
            self.textEdit = SignalTextEdit('', self)
            self.textEdit.setFixedSize(self.size())
            self.textEdit.editFinished.connect(self.edit_finished)
        self.textEdit.setVisible(True)
        self.textEdit.setText(self.data_value)
        self.textEdit.selectAll()
        self.textLabel.setVisible(False)

    def set_no_editable(self):
        if self.textEdit is not None:
            self.data_value = self.textEdit.toPlainText()
            self.textEdit.setVisible(False)
        self.textLabel.setVisible(True)
        self.textLabel.setText(self.data_value)

    def resizeEvent(self, *args, **kwargs):
        self.set_size()
        super(CellTextEdit, self).resizeEvent(*args, **kwargs)

    def set_size(self):
        # self.textEdit.document().adjustSize()
        self.textLabel.setFixedWidth(self.width())
        textHeight = self.textLabel.document().size().height()
        self.setFixedHeight(textHeight + 10)
        self.textLabel.setFixedHeight(textHeight + 10)
        self.targetHeight = textHeight + 10
        # print self.treeitem
        # self.treeitem.setSizeHint(0, QSize(self.width(), self.height()))


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


# thumbnail
class CellThumbnail(CellWidget):
    def __init__(self, **kwargs):
        super(CellThumbnail, self).__init__(**kwargs)

        self.autoHeight = True

        self.thumbnailPath = ''
        self.thumbnailLabel = ThumbnailLabel(dynamic=False, background='transparent', parent=self)

    def set_value(self, value):
        if value is not None:
            self.thumbnailPath = value
            self.thumbnailLabel.create_preview(self.thumbnailPath)
            self.thumbnailLabel.cacheDone.connect(self.load_done)

    def load_done(self):
        self.set_size()
        # print 'load done'
        self.treeitem.tree.section_resized(index=self.column)
        # self.treeitem.tree.updateGeometries()

    def resizeEvent(self, *args, **kwargs):
        super(CellThumbnail, self).resizeEvent(*args, **kwargs)
        self.set_size()

    def set_size(self):
        self.thumbnailLabel.setFixedWidth(self.width())
        self.thumbnailLabel.set_resize_size()
        targetHeight = self.thumbnailLabel.targetHeight
        self.thumbnailLabel.setFixedHeight(targetHeight)
        self.setFixedHeight(targetHeight)
        self.targetHeight = targetHeight


# bool
class CellBoolEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellBoolEdit, self).__init__(**kwargs)

        self.trueText = 'true'
        self.falseText = 'false'

        self.statusLabel = QLabel(self)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.boolCheck = None

        self.data_value = False

        self.set_no_editable()

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            self.statusLabel.setText(self.trueText if value else self.falseText)

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
        self.statusLabel.setText(self.trueText if self.data_value else self.falseText)
        self.statusLabel.setVisible(True)

    def resizeEvent(self, *args, **kwargs):
        super(CellBoolEdit, self).resizeEvent(*args, **kwargs)
        self.statusLabel.setFixedWidth(self.width())


class ActiveBoolEdit(CellBoolEdit):
    def __init__(self, **kwargs):
        super(ActiveBoolEdit, self).__init__(**kwargs)
        self.trueText = '<font color=green>active</font>'
        self.falseText = '<font color=red><SPAN style="TEXT-DECORATION: line-through">active</SPAN></font>'


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


# choose
def get_choose(choose_list, value):
    for i in choose_list:
        if i.value == value:
            return i
    return None


class ChooseModel(object):
    def __init__(self,
                 value='',
                 display_text=None,
                 choose_text_list=[],
                 icon=None,
                 color=None,
                 tooltip=None):
        super(ChooseModel, self).__init__()
        self.value = value
        self.display_text = display_text if display_text is not None else value
        self.choose_text_list = choose_text_list
        self.icon = icon
        self.color = color
        self.tooltip = tooltip if tooltip is not None else value

    def __cmp__(self, other):
        return cmp(self.value, other.value)


class ChooseItem(QWidget):
    choose = Signal(str)
    def __init__(self, value, text_list=[], icon=None, icon_size=40, parent=None):
        """
        :param value: str
        :param text_list: [{'text':'', 'width':40}, {}]
        :param icon: str
        :param parent:
        """
        super(ChooseItem, self).__init__(parent)
        self.value = value

        self.masterLayout = QHBoxLayout()
        # if icon is not None:
        self.icon = QLabel()
        self.icon.setFixedSize(icon_size, icon_size)
        if icon is not None and os.path.exists(icon):
            self.icon.setPixmap(resource.get_pixmap(icon, scale=icon_size))
        self.masterLayout.addWidget(self.icon)
        if icon is not None:
            self.masterLayout.insertSpacing(0, 10)
            self.masterLayout.insertSpacing(2, 10)
        for text in text_list:
            label = QLabel(text['text'])
            if text['width'] is not None:
                label.setFixedWidth(text['width'])
            self.masterLayout.addWidget(label)
        self.masterLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.masterLayout)

    def mouseReleaseEvent(self, *args, **kwargs):
        self.choose.emit(self.value)


class CellChooseEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellChooseEdit, self).__init__(**kwargs)

        self.iconSize = 20

        self.iconLabel = QLabel()
        self.iconLabel.setFixedSize(self.iconSize, self.iconSize)
        self.textLabel = QLabel()
        self.masterLayout = QHBoxLayout()
        self.masterLayout.setContentsMargins(0, 0, 0, 0)
        self.masterLayout.setAlignment(Qt.AlignLeft)
        self.masterLayout.addWidget(self.iconLabel)
        self.masterLayout.addWidget(self.textLabel)
        self.setLayout(self.masterLayout)

        self.combo = None

        self.data_value = ''
        self.chooseList = None
        self.chooseListFunc = ''
        self.chooseListFuncArgs = {}
        self.comboWidth = 200
        self.comboHeight = 50
        self.comboIconSize = 40

    def apply_choose(self, choose):
        if choose:
            display_text = choose.display_text
            icon = choose.icon
            color = choose.color
            # print color
            self.textLabel.setText(display_text)
            if icon is not None and os.path.exists(icon):
                self.iconLabel.setPixmap(resource.get_pixmap(icon, scale=self.iconSize))
            if color is not None:
                r, g, b, a = int10_to_rgb(color, max=255, alpha_index=0)
                # print r, g, b, a
                self.back.setStyleSheet('background:rgb({}, {}, {}, {})'.format(r, g, b, 100))
            self.setToolTip(choose.tooltip)
        else:
            self.textLabel.setText(value)

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            choose = get_choose(self.chooseList, value)
            self.apply_choose(choose)

    def set_editable(self):
        self.combo = QComboBox(self)
        self.comboListWidget = QListWidget()
        self.combo.setModel(self.comboListWidget.model())
        self.combo.setView(self.comboListWidget)
        self.comboListWidget.setStyleSheet(scrollbar_style)
        self.combo.setStyleSheet("""
        *{
            outline:0px;
            /*border:none;*/
        }
        QAbstractItemView{
            min-width:%spx;
            border:none;
        }
        QAbstractItemView::item{
            height:%spx;
        }
        QListView::item{
            background:white;
        }
        QListView::item:hover{
            background:rgb(200,200,200);
        }
        """ % (self.comboWidth, self.comboHeight))
        self.comboListWidget.clear()
        self.chooseList = get_class_from_name_data(__name__, self.chooseListFunc)(**self.chooseListFuncArgs)
        self.chooseList.sort()
        for choose in self.chooseList:
            listItemWidget = ChooseItem(value=choose.value,
                                        text_list=choose.choose_text_list,
                                        icon=choose.icon,
                                        icon_size=self.comboIconSize)
            listItemWidget.choose.connect(self.choose_item)
            listItem = QListWidgetItem()
            self.comboListWidget.addItem(listItem)
            self.comboListWidget.setItemWidget(listItem, listItemWidget)
        self.combo.setFixedSize(self.width(), self.height())
        self.combo.showPopup()

    def choose_item(self, value):
        self.data_value = value
        choose = get_choose(self.chooseList, value)
        self.apply_choose(choose)
        self.edit_finished()

    def set_no_editable(self):
        self.combo.hidePopup()


def get_sex_choose_list():
    return [
        ChooseModel(value='male',
                    choose_text_list=[{'text':'male', 'width':None}],
                    icon=resource.get_pic('icon', 'male.png')),
        ChooseModel(value='female',
                    choose_text_list=[{'text':'female', 'width':None}],
                    icon=resource.get_pic('icon', 'female.png')),
    ]


SexChooseList = get_sex_choose_list()


class SexChooseEdit(CellChooseEdit):
    def __init__(self, **kwargs):
        super(SexChooseEdit, self).__init__(**kwargs)
        self.iconLabel.setVisible(False)
        self.masterLayout.insertSpacing(1, 5)
        self.chooseList = SexChooseList
        self.chooseListFunc = 'get_sex_choose_list'
        self.comboWidth = 100
        self.comboHeight = 30
        self.comboIconSize = 20


def get_department_choose_list():
    choose_list = []
    for department in Department.select():
        name = department.name
        full_name = department.full_name
        color = department.color
        choose_list.append(ChooseModel(
            value=name,
            choose_text_list=[{'text': name, 'width': 40}, {'text': full_name, 'width': None}],
            color=color,
            icon=resource.get_pic('icon', 'Departments.png'),
            tooltip=full_name)
        )
    return choose_list


DepartmentChooseList = get_department_choose_list()


class DepartmentChooseEdit(CellChooseEdit):
    def __init__(self, **kwargs):
        super(DepartmentChooseEdit, self).__init__(**kwargs)
        # self.iconLabel.setVisible(False)
        # self.masterLayout.insertSpacing(1, 5)
        self.chooseList = DepartmentChooseList
        self.chooseListFunc = 'get_department_choose_list'
        self.comboWidth = 200
        self.comboHeight = 30
        self.comboIconSize = 10


def get_permission_group_choose_list():
    choose_list = []
    for permission in PermissionGroup.select():
        name = permission.name
        choose_list.append(ChooseModel(
            value=name,
            choose_text_list=[{'text': name, 'width': None}],
        )
        )
    return choose_list


PermissionGroupChooseList = get_permission_group_choose_list()


class PermissionGroupChooseEdit(CellChooseEdit):
    def __init__(self, **kwargs):
        super(PermissionGroupChooseEdit, self).__init__(**kwargs)
        self.iconLabel.setVisible(False)
        self.masterLayout.insertSpacing(1, 5)
        self.chooseList = PermissionGroupChooseList
        self.chooseListFunc = 'get_permission_group_choose_list'
        self.comboWidth = 120
        self.comboHeight = 30
        self.comboIconSize = 10


# def get_project_status_choose_list():
#     choose_list = []
#     for status in Status.select():
#         name = status.name
#         full_name = status.full_name
#         color = status.color
#         icon = status.icon
#         choose_list.append(ChooseModel(
#             value=name,
#             choose_text_list=[{'text': name, 'width': 50}, {'text': full_name, 'width': None}],
#             color=color,
#             icon=icon,
#         )
#         )
#     return choose_list


def get_all_status():
    choose_list = {}
    for status in Status.select():
        for model in ['Project', 'Sequence', 'Shot', 'Asset', 'Task', 'Version']:
            if model not in choose_list.keys():
                choose_list[model] = []
            if status.referred_table.find(model) != -1:
                name = status.name
                full_name = status.full_name
                color = status.color
                icon = status.icon
                choose_list[model].append(ChooseModel(
                    value=name,
                    choose_text_list=[{'text': name, 'width': 50}, {'text': full_name, 'width': None}],
                    color=color,
                    icon=icon,
                )
                )
    return choose_list

all_status_choose = get_all_status()


def get_status_choose_list(model=''):
    if model in all_status_choose:
        return all_status_choose[model]


loaded_project_status = get_status_choose_list(model='Project')
loaded_sequence_status = get_status_choose_list(model='Sequence')
loaded_shot_status = get_status_choose_list(model='Shot')
loaded_asset_status = get_status_choose_list(model='Asset')
loaded_task_status = get_status_choose_list(model='Task')
loaded_version_status = get_status_choose_list(model='Version')


class StatusChooseEdit(CellChooseEdit):
    def __init__(self, model=None, **kwargs):
        super(StatusChooseEdit, self).__init__(**kwargs)
        self.textLabel.setVisible(False)
        self.masterLayout.insertSpacing(1, 5)
        self.masterLayout.setAlignment(Qt.AlignCenter)
        # self.chooseList = get_status_choose_list()
        self.chooseListFunc = 'get_status_choose_list'
        self.chooseListFuncArgs = {'model':model}
        self.chooseList = get_class_from_name_data('sins.ui.widgets.table.cell_edit',
                                                              'loaded_{}_status'.
                                                              format(model.lower()))
        self.comboWidth = 250
        self.comboHeight = 50
        self.comboIconSize = 20


# class ProjectStatusChooseEdit(StatusChooseEdit):
#     def __init__(self, **kwargs):
#         super(ProjectStatusChooseEdit, self).__init__(**kwargs)
#         self.chooseListFuncArgs = {'model': 'Project'}
#         self.chooseList = loaded_project_status
#
#
# class ShotStatusChooseEdit(StatusChooseEdit):
#     def __init__(self, **kwargs):
#         super(ShotStatusChooseEdit, self).__init__(**kwargs)
#         self.chooseListFuncArgs = {'model': 'Shot'}
#         self.chooseList = loaded_shot_status
#
#
# class SequenceStatusChooseEdit(StatusChooseEdit):
#     def __init__(self, **kwargs):
#         super(SequenceStatusChooseEdit, self).__init__(**kwargs)
#         self.chooseListFuncArgs = {'model': 'Sequence'}
#         self.chooseList = loaded_sequence_status
#
#
# class AssetStatusChooseEdit(StatusChooseEdit):
#     def __init__(self, **kwargs):
#         super(AssetStatusChooseEdit, self).__init__(**kwargs)
#         self.chooseListFuncArgs = {'model': 'Asset'}
#         self.chooseList = loaded_asset_status
#
#
# class TaskStatusChooseEdit(StatusChooseEdit):
#     def __init__(self, **kwargs):
#         super(TaskStatusChooseEdit, self).__init__(**kwargs)
#         self.chooseListFuncArgs = {'model': 'Task'}
#         self.chooseList = loaded_task_status
#
#
# class VersionStatusChooseEdit(StatusChooseEdit):
#     def __init__(self, **kwargs):
#         super(VersionStatusChooseEdit, self).__init__(**kwargs)
#         self.chooseListFuncArgs = {'model': 'Version'}
#         self.chooseList = loaded_version_status


class TextBrowser(QTextBrowser):
    def __init__(self, *args, **kwargs):
        super(TextBrowser, self).__init__(*args, **kwargs)

        self.setOpenLinks(False)
        self.setStyleSheet("""
        *{
        border:none;
        background:transparent;
        }
        """)

    def loadResource(self, type, name):
        # super(TextBrowser, self).loadResource(type, name)
        # print type, name
        return


class CellSingleObjectEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellSingleObjectEdit, self).__init__(**kwargs)

        self.label = QLabel('', self)
        self.label.setOpenExternalLinks(False)
        self.label.linkActivated.connect(self.open_new_page)
        # self.label = TextBrowser(self)

    def set_value(self, value):
        label = value['label']
        db_object = value['object']
        if db_object is not None:
            text = ''
            if hasattr(db_object, 'icon'):
                text += '<img src="{icon}" width={size} height={size}>'.format(
                    icon=db_object.icon,
                    size=OBJECT_ICON_SIZE
                )
            text += '<a href="{url}">{label}</a>'.format(
                url='test',
                label=label
            )
            if hasattr(db_object, 'status'):
                status = db_object.status
                loaded_status_list = get_class_from_name_data('sins.ui.widgets.table.cell_edit',
                                                              'loaded_{}_status'.
                                                              format(db_object.__class__.__name__.lower()))
                status_icon = get_choose(loaded_status_list, status).icon
                if status_icon is not None and os.path.exists(status_icon):
                    text += '<img src="{icon}" width={size} height={size}>'.format(
                        icon=status_icon,
                        size=OBJECT_ICON_SIZE
                    )
            # text += '<img src="{}">'.format(db_object.icon)
            # print text
            self.label.setText(text)

    def open_new_page(self, url):
        print 'open page:', url
        current_parent = self.parent()
        while current_parent.parent() is not None:
            current_parent = current_parent.parent()
        # print current_parent
        if hasattr(current_parent, 'to_page'):
            current_parent.to_page(url)
        # self.link.emit(url)


class RemoveLabelButton(QLabel):
    clicked = Signal()
    def __init__(self, parent=None):
        super(RemoveLabelButton, self).__init__(parent)
        self.setPixmap(resource.get_pixmap("button", "close_darkgray.png", scale=15))
        self.setFixedSize(15, 15)

    def mouseReleaseEvent(self, *args, **kwargs):
        self.clicked.emit()


class SingleObjectWidget(QWidget):
    def __init__(self, db_object, label_attr):
        super(SingleObjectWidget, self).__init__()

        self.db_object = db_object

        self.backLabel = QLabel(self)
        self.backLabel.setStyleSheet("""
        background: rgb(200, 200, 230);
        border-radius:13px
        """)
        self.objectLabel = QLabel(getattr(self.db_object, label_attr))
        self.removeButton = RemoveLabelButton(parent=self)
        self.masterLayout = QHBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignCenter)
        self.masterLayout.setContentsMargins(10, 5, 10, 5)
        self.masterLayout.addWidget(self.objectLabel)
        self.masterLayout.addWidget(self.removeButton)
        self.setLayout(self.masterLayout)

        self.setFixedHeight(26)

    def resizeEvent(self, *args, **kwargs):
        super(SingleObjectWidget, self).resizeEvent(*args, **kwargs)
        self.backLabel.setFixedSize(self.size())


class MultiObjectEditWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(MultiObjectEditWidget, self).__init__(*args, **kwargs)

        self.db_object_list = []
        self.init_ui()

    def init_ui(self):

        self.setWindowFlags(Qt.Popup)

        self.objectsWidget = QWidget()
        self.objectsLayout = FlowLayout(spacing=10, margin=10, parent=self.objectsWidget)
        self.objectsWidget.setLayout(self.objectsLayout)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.objectsWidget)
        self.scrollArea.setWidgetResizable(True)

        self.lineEdit = QLineEdit()

        self.buttonLayout = QHBoxLayout()
        self.applyButton = QPushButton('Apply')
        self.cancelButton = QPushButton('Cancel')
        self.buttonLayout.setAlignment(Qt.AlignRight)
        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(self.scrollArea)
        self.masterLayout.addWidget(self.lineEdit)
        self.masterLayout.addLayout(self.buttonLayout)
        self.setLayout(self.masterLayout)

        self.resize(400, 300)

        self.setStyleSheet("""
        QScrollArea, QLineEdit{
            border:none;
        }
        """)

        self.applyButton.clicked.connect(self.apply_clicked)
        self.cancelButton.clicked.connect(self.close)

    def set_value(self, db_objects_dict):
        db_objects = db_objects_dict['objects']
        label_attr = db_objects_dict['object_label_attr']
        if db_objects is None:
            db_objects = []
        print db_objects
        for db_object in db_objects:
            singleObjectWidget = SingleObjectWidget(db_object, label_attr)
            singleObjectWidget.removeButton.clicked.connect(self.remove_object)
            self.objectsLayout.addWidget(singleObjectWidget)
            self.db_object_list.append(db_object)

    def add_object(self):
        pass

    def remove_object(self):
        singleObjectWidget = self.sender().parent()
        db_object = singleObjectWidget.db_object
        index = self.db_object_list.index(db_object)
        print index
        singleObjectWidget.setParent(None)
        self.objectsLayout.removeWidget(singleObjectWidget)
        self.db_object_list.remove(db_object)

    def apply_clicked(self):
        self.close()


class CellMultiObjectEdit(CellWidget):
    def __init__(self, linkable=True, link_model=None, **kwargs):
        super(CellMultiObjectEdit, self).__init__(**kwargs)

        self.linkable = linkable
        self.link_model_name = link_model

        self.label = TextBrowser(self)
        self.label.anchorClicked.connect(self.open_new_page)

        self.edit_widget = None

    def set_value(self, value):
        self.data_value = value
        label_attr = value['object_label_attr']
        db_objects = value['objects']
        # print db_objects
        # if self.link_model_name == 'Project':
        #     self_projects = current_user_object.projects
        #     db_object_query = db_object_query.select().where(Project.id.in_(self_projects))
        if db_objects is not None:
            text = ''
            for db_object in db_objects:
                # print db_object
                if hasattr(db_object, 'icon'):
                    text += '<img src="{icon}" width={size} height={size}>'.format(
                        icon=db_object.icon,
                        size=OBJECT_ICON_SIZE
                    )
                if self.linkable:
                    text += '<a href="{url}"><font color=#404040>{label}</font></a>'.format(
                        url='test',
                        label=getattr(db_object, label_attr)
                    )
                else:
                    text += '<font color=#404040>{label}</font>'.format(
                        label=getattr(db_object, label_attr)
                    )
                if hasattr(db_object, 'status'):
                    status = db_object.status
                    loaded_status_list = get_class_from_name_data('sins.ui.widgets.table.cell_edit',
                                                                  'loaded_{}_status'.
                                                                  format(db_object.__class__.__name__.lower()))
                    status_icon = get_choose(loaded_status_list, status).icon
                    if status_icon is not None and os.path.exists(status_icon):
                        text += '<img src="{icon}" width={size} height={size}>'.format(
                            icon=status_icon,
                            size=OBJECT_ICON_SIZE
                        )
                text += ', '
            self.label.setText(text)

    def set_editable(self):
        if self.edit_widget is None:
            self.edit_widget = MultiObjectEditWidget(self.treeitem.tree)
        self.edit_widget.set_value(self.data_value)
        screen_size = get_screen_size()
        self.edit_widget.move((screen_size.width() - self.edit_widget.width()) / 2,
                            (screen_size.height() - self.edit_widget.height()) / 2)

        self.edit_widget.show()

    def open_new_page(self, url):
        print 'open page:', url
        current_parent = self.parent()
        while current_parent.parent() is not None:
            current_parent = current_parent.parent()
        # print current_parent
        if hasattr(current_parent, 'to_page'):
            current_parent.to_page(url)
        # self.link.emit(url)




if __name__ == '__main__':
    import time

    app = QApplication(sys.argv)

    widget = MultiObjectEditWidget()
    widget.set_value({'objects': Project.get(id=1).persons, 'object_label_attr': 'user_login'})
    widget.show()

    app.exec_()