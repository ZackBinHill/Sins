# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import *
from sins.module.time_utils import current_time
from sins.db.models import *


logger = get_logger(__name__)

EDITLABEL_SIZE = 20


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
                 db_instance=None,
                 model_attr='',
                 column_label='',
                 parent=None):
        super(CellWidget, self).__init__(parent)
        self.editable = editable
        self.treeitem = treeitem
        self.column = column
        self.column_label = column_label
        self.db_instance = db_instance
        self.model_attr = model_attr
        self.autoHeight = False
        self.targetHeight = 0

        self.data_value = None
        self.update_db_time = 0
        self.has_edit_label = False

        # self.setStyleSheet("border:none;background:transparent")
        self.back = QLabel(self)
        # self.back.setStyleSheet("background:rgb(100, 140, 100, 250)")
        self.setMinimumHeight(22)

    def add_front(self, editlabel=True):
        self.has_edit_label = editlabel

    def set_value(self, value):
        pass

    def set_db_instance(self, db_instance):
        self.db_instance = db_instance

    def set_read_only(self, editable=False):
        self.editable = editable

    def set_editable(self):
        pass

    def set_no_editable(self):
        pass

    def edit_finished(self):
        self.set_no_editable()
        if current_time() - self.update_db_time > 0.01:
            # print self.db_instance, self.model_attr
            if self.db_instance is not None and (hasattr(self.db_instance, self.model_attr)):
                old_value = getattr(self.db_instance, self.model_attr)
                logger.debug(u'setattr({}, {}, {})'.format(self.db_instance, self.model_attr, self.data_value))
                setattr(self.db_instance, self.model_attr, self.data_value)
                self.db_instance.save()
                detail = u'update {column} from {old} to {new}'.format(column=self.column_label,
                                                                        old=old_value,
                                                                        new=self.data_value)
                LogTable.create(
                    table_name=self.db_instance._meta.table_name,
                    event='UPDATE',
                    event_date=datetime.datetime.now(),
                    event_data_id=self.db_instance.id,
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
