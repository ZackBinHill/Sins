# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import *
from .basic import CellWidget
from sins.ui.utils.const import scrollbar_style


# line edit
class CellLineEdit(CellWidget):
    def __init__(self, password_mode=False, **kwargs):
        super(CellLineEdit, self).__init__(**kwargs)

        self.password_mode = password_mode

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
            if self.password_mode:
                self.textLabel.setText('******')

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
            # self.data_value = u'{}'.format(self.lineEdit.text())
            self.data_value = to_unicode(self.lineEdit.text())
            if self.is_float:
                self.data_value = float(self.data_value)
            if self.is_int:
                self.data_value = int(self.data_value)
            self.lineEdit.setVisible(False)
        self.textLabel.setVisible(True)
        # self.textLabel.setText(str(self.data_value))
        self.textLabel.setText(u'{}'.format(self.data_value))
        if self.password_mode:
            self.textLabel.setText('******')

    def resizeEvent(self, *args, **kwargs):
        super(CellLineEdit, self).resizeEvent(*args, **kwargs)
        if self.lineEdit is not None:
            self.lineEdit.setFixedWidth(self.width())
        self.textLabel.setFixedWidth(self.width())


# class PasswordEdit(CellLineEdit):
#     def __init__(self, **kwargs):
#         super(PasswordEdit, self).__init__(**kwargs)
#         self.textLabel.setText('******')
#     def set_value(self, value):
#         pass


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

