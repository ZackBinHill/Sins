# -*- coding: utf-8 -*-

import datetime
import os
import sys
import webbrowser
from BQt import QtWidgets, QtCore, QtGui
from bfx_resources.icons import ICON_DIR
from bfx.ui import get_pixmap
from bfx.data.prod.shotgun.production2.models import Note, Reply
from bfx.ui.component import FlowLayout


USER_ICON_SIZE = 40
ATTACHMENT_WIDTH = 200
TIME_DELTA = datetime.timedelta(hours=8)


def get_link_color(text_color):
    link_color_red = text_color.red() + 10 if text_color.red() > 125 else text_color.red() + 100
    link_color_green = text_color.green() + 10 if text_color.green() > 125 else text_color.green() + 100
    link_color_blue = 255 if text_color.blue() > 125 else 200
    link_color_red = min(link_color_red, 220)
    link_color_green = min(link_color_green, 220)
    return link_color_red, link_color_green, link_color_blue


class AutoResizeTextEdit(QtWidgets.QTextBrowser):
    def __init__(self, *args, **kwargs):
        super(AutoResizeTextEdit, self).__init__(*args, **kwargs)

        self.setReadOnly(True)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.open_link)

    def open_link(self, url):
        # print url.toString()
        webbrowser.open(url.toString())

    def set_size(self):
        target_height = self.document().size().height()
        self.setFixedHeight(target_height + 5.0)

    def resizeEvent(self, event):
        super(AutoResizeTextEdit, self).resizeEvent(event)
        self.set_size()


class LabelButton(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, name='', icon=None, *args, **kwargs):
        super(LabelButton, self).__init__(*args, **kwargs)

        self.setToolTip(name)
        self.setMouseTracking(True)
        self.setFixedSize(20, 20)
        if icon is not None:
            if isinstance(icon, (basestring, str)) and os.path.exists(icon):
                self.setPixmap(QtGui.QPixmap(icon))
            elif isinstance(icon, QtGui.QPixmap):
                self.setPixmap(icon)
        self.setAlignment(QtCore.Qt.AlignCenter)

    def enterEvent(self, event):
        super(LabelButton, self).enterEvent(event)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        super(LabelButton, self).mouseReleaseEvent(event)
        self.clicked.emit()


class UserIconLabel(QtWidgets.QLabel):
    def __init__(self, icon=None, user=None, *args, **kwargs):
        super(UserIconLabel, self).__init__(*args, **kwargs)

        self.setFixedSize(USER_ICON_SIZE, USER_ICON_SIZE)

        if user is not None:
            self.set_user(user)
        elif icon is not None:
            self.set_icon(icon)

    def set_user(self, user):
        icon = os.path.join(ICON_DIR, 'notification', 'svg', 'ic_adb_48px.svg')
        if user is not None:
            if hasattr(user, 'thumbnail'):
                user_thumbnail = user.thumbnail
                if user_thumbnail is not None and os.path.exists(user_thumbnail.hosted_path):
                    icon = user_thumbnail.hosted_path
                else:
                    icon = os.path.join(ICON_DIR, 'action', 'svg', 'ic_face_48px.svg')
        self.set_icon(icon)

    def set_icon(self, icon):
        if icon.endswith('.svg'):
            self.setPixmap(get_pixmap(icon).scaled(USER_ICON_SIZE,
                                                      USER_ICON_SIZE,
                                                      QtCore.Qt.KeepAspectRatioByExpanding,
                                                      QtCore.Qt.SmoothTransformation,
                                                      ))
        else:
            self.setPixmap(QtGui.QPixmap(icon).scaled(USER_ICON_SIZE,
                                                      USER_ICON_SIZE,
                                                      QtCore.Qt.KeepAspectRatioByExpanding,
                                                      QtCore.Qt.SmoothTransformation,
                                                      ))

    def paintEvent(self, event):
        if self.pixmap() is not None:
            painter = QtGui.QPainter(self)
            painter.setRenderHints(QtGui.QPainter.Antialiasing, True)

            path = QtGui.QPainterPath()
            path.addEllipse(0, 0, self.width(), self.height())
            painter.setClipPath(path)

            painter.drawPixmap(0, 0, self.pixmap())


class AttachmentLabel(QtWidgets.QLabel):
    def __init__(self, file_path, content_type='', *args, **kwargs):
        super(AttachmentLabel, self).__init__(*args, **kwargs)

        self.file_path = file_path
        if content_type.startswith('image'):
            pixmap = QtGui.QPixmap(file_path)
            if pixmap.width() > 0:
                pixmap = pixmap.scaledToWidth(min(pixmap.width(), ATTACHMENT_WIDTH), QtCore.Qt.SmoothTransformation)
                self.setPixmap(pixmap)
            else:
                self.setText(os.path.basename(file_path))
        else:
            self.setText(os.path.basename(file_path))

        # self.setStyleSheet("""
        # QLabel{
        # text-decoration:underline;
        # }
        # """)

        # self.setMouseTracking(True)
        self.setToolTip('Click to view')

    def enterEvent(self, event):
        super(AttachmentLabel, self).enterEvent(event)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        super(AttachmentLabel, self).mouseReleaseEvent(event)
        # print 'view:', self.file_path
        webbrowser.open(self.file_path)

    def paintEvent(self, event):
        super(AttachmentLabel, self).paintEvent(event)
        if self.text() != '':
            painter = QtGui.QPainter(self)
            painter.drawLine(QtCore.QPoint(0, self.height() - 1),
                             QtCore.QPoint(self.width(), self.height() - 1))


class AddAttachmentWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(AddAttachmentWidget, self).__init__(*args, **kwargs)


class AddNoteTextEdit(QtWidgets.QTextEdit):
    changed = QtCore.pyqtSignal()
    cancelNote = QtCore.pyqtSignal()
    applyNote = QtCore.pyqtSignal(str)

    def __init__(self, attachable=True, *args, **kwargs):
        super(AddNoteTextEdit, self).__init__(*args, **kwargs)

        self.attachable = attachable
        attach_icon = get_pixmap(os.path.join(ICON_DIR, 'file', 'svg', 'ic_attachment_24px.svg'), size=[20, 20])
        self.attachButton = LabelButton(name='Attachment', icon=attach_icon, parent=self)
        self.attachButton.setFixedSize(20, 20)
        self.attachButton.setVisible(attachable)
        self.attach_files = []

        self.cancelButton = QtWidgets.QPushButton('Cancel', self)
        self.applyButton = QtWidgets.QPushButton('Apply', self)
        for button in [self.applyButton, self.cancelButton]:
            button.setFixedSize(50, 20)
            button.setStyleSheet("""
            QPushButton{
                border: none;
                border: 1px solid rgb(200, 200, 220);
                border-radius: 2px;
            }
            """)

        self.setStyleSheet("""
        QTextEdit{
            border: 1px solid rgb(200, 200, 220);
            border-radius: 5px;
        }
        """)

        self.setFixedWidth(350)

        self.set_editable(False)

        self.applyButton.clicked.connect(self.apply_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)
        self.attachButton.clicked.connect(self.attach_clicked)

    def mouseReleaseEvent(self, event):
        super(AddNoteTextEdit, self).mouseReleaseEvent(event)
        self.self_clicked()

    def self_clicked(self):
        if self.isReadOnly():
            self.set_editable(True)

    def set_editable(self, editable=True, emit_change=True):
        if editable:
            self.setFixedHeight(80)
            self.clear()
        else:
            self.setFixedHeight(50)
            self.setText('Click to add a note')
        self.setReadOnly(not editable)
        self.set_pos()
        if emit_change:
            self.changed.emit()
        self.setFocus()
        self.applyButton.setVisible(editable)
        self.cancelButton.setVisible(editable)
        self.attachButton.setVisible(self.attachable and editable)

    def apply_clicked(self):
        content = self.toPlainText()
        self.set_editable(False, emit_change=False)
        self.applyNote.emit(content)
        self.attach_files = []

    def cancel_clicked(self):
        self.set_editable(False)
        self.cancelNote.emit()
        self.attach_files = []

    def attach_clicked(self):
        # print 'add attachment'
        result = QtWidgets.QFileDialog.getOpenFileNames(None, "Select attachment files", ".")
        if isinstance(result, tuple):
            result = result[0]
        for i in result:
            if not isinstance(i, (basestring, str)):
                i = str(i.toUtf8())
            self.attach_files.append(i)
        # print self.attach_files

    def set_pos(self):
        self.applyButton.move(self.width() - self.applyButton.width(),
                              self.height() - self.applyButton.height())
        self.cancelButton.move(self.applyButton.pos().x() - self.cancelButton.width(),
                               self.height() - self.cancelButton.height())
        self.attachButton.move(0,
                               self.height() - self.attachButton.height())

    def resizeEvent(self, event):
        super(AddNoteTextEdit, self).resizeEvent(event)
        self.set_pos()


class AttachmentsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(AttachmentsWidget, self).__init__()

        self.masterLayout = FlowLayout(spacing=20, margin=[53, 5])
        self.setLayout(self.masterLayout)

    def add_widget(self, widget):
        self.masterLayout.addWidget(widget)


class _BaseNoteWidget(QtWidgets.QWidget):
    def __init__(self, note=None, text_color=None, *args, **kwargs):
        super(_BaseNoteWidget, self).__init__(*args, **kwargs)

        if isinstance(note, (basestring, int)):
            self.note_object = Note.get(id=note)
        else:
            self.note_object = note

        self.note_user = None
        self.note_user_name = 'PLE'
        try:
            self.note_user = self.note_object.user
            self.note_user_name = self.note_user.name
        except:
            pass

        self.note_date = self.note_object.date_created + TIME_DELTA
        self.note_content = self.note_object.content if self.note_object.content is not None else ''

        self.text_color = QtWidgets.QApplication.palette().text().color() if text_color is None else text_color

    def init_ui(self):
        self.user_icon_layout = QtWidgets.QVBoxLayout()
        self.user_icon = UserIconLabel()
        self.user_icon.set_user(self.note_user)
        self.user_icon_layout.setAlignment(QtCore.Qt.AlignTop)
        self.user_icon_layout.addWidget(self.user_icon)

        self.note_layout = QtWidgets.QVBoxLayout()
        self.note_layout.setAlignment(QtCore.Qt.AlignTop)
        self.note_layout.setSpacing(0)
        self.user_time_layout = QtWidgets.QHBoxLayout()
        self.user_time_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.user_time_layout.addSpacing(4)
        self.note_user_name_label = QtWidgets.QLabel(self.note_user_name)
        self.user_time_layout.addWidget(self.note_user_name_label)
        self.user_time_layout.addSpacing(15)
        note_date_label = QtWidgets.QLabel(self.note_date.strftime('%Y-%m-%d %H:%M:%S'))
        note_date_label.setStyleSheet('color: rgb({}, {}, {}, 125)'.format(self.text_color.red(),
                                                                           self.text_color.green(),
                                                                           self.text_color.blue(), ))
        self.user_time_layout.addWidget(note_date_label)
        self.note_content_edit = AutoResizeTextEdit()
        self.note_content_edit.setText(u'{content}'.format(content=self.note_content))
        self.note_layout.addLayout(self.user_time_layout)
        self.note_layout.addWidget(self.note_content_edit)

        self.current_note_layout = QtWidgets.QHBoxLayout()
        self.current_note_layout.addLayout(self.user_icon_layout)
        self.current_note_layout.addSpacing(5)
        self.current_note_layout.addLayout(self.note_layout)

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                 QtWidgets.QSizePolicy.Maximum))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.text_color.red(),
                                                   self.text_color.green(),
                                                   self.text_color.blue(),
                                                   20)))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 5, 5)
        super(_BaseNoteWidget, self).paintEvent(event)


class ReplyWidget(_BaseNoteWidget):
    def __init__(self, *args, **kwargs):
        super(ReplyWidget, self).__init__(*args, **kwargs)

        self.init_ui()

    def init_ui(self):
        super(ReplyWidget, self).init_ui()
        self.setLayout(self.current_note_layout)


class NoteWidget(_BaseNoteWidget):
    def __init__(self, current_user=None, attachments=[], *args, **kwargs):
        super(NoteWidget, self).__init__(*args, **kwargs)

        self.current_user = current_user
        self.note_subject = self.note_object.subject
        self.children = self.note_object.replies_prefetch if hasattr(self.note_object, 'replies_prefetch') else []
        # self.children = self.note_object.replies
        # self.attachments = self.note_object.attachments
        self.attachments = attachments

        self.init_ui()
        self.show_attachments()
        self.expand_children()

    def init_ui(self):
        super(NoteWidget, self).init_ui()

        link_color_red, link_color_green, link_color_blue = get_link_color(self.text_color)
        # print link_color_red, link_color_green, link_color_blue
        self.note_content_edit.setText(u"""
        <div style="margin-bottom: 8px"><a href="{url}"><font color=#{color}>{subject}</font></a></div>
        <div>{content}</div>
        """.format(url=self.note_object.url,
                   color='%02x%02x%02x' % (link_color_red,
                                           link_color_green,
                                           link_color_blue),
                   subject=self.note_subject,
                   content=self.note_content.replace('\n', '<br/>')))

        self.attachments_widget = AttachmentsWidget()

        self.children_layout = QtWidgets.QVBoxLayout()
        self.children_layout.setAlignment(QtCore.Qt.AlignTop)
        self.children_layout.setContentsMargins(20, 0, 0, 0)

        self.reply_button = QtWidgets.QPushButton('Reply', self)
        self.reply_button.setFixedWidth(50)
        self.reply_button.setFixedHeight(22)
        self.reply_button.setVisible(False)
        self.reply_button.setStyleSheet("""
        QPushButton{
            background: transparent;
            border: none;
            border-radius: 3px;
            outline: 0px;
        }
        QPushButton:hover{
            background: rgb(100, 100, 100, 50);
        }
        QPushButton:pressed{
            background: rgb(100, 100, 100, 70);
        }

        """)

        self.reply_layout = QtWidgets.QHBoxLayout()
        self.reply_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.reply_layout.setContentsMargins(50, 0, 0, 0)
        self.reply_edit = None

        self.masterLayout = QtWidgets.QVBoxLayout()
        self.masterLayout.setAlignment(QtCore.Qt.AlignTop)
        self.masterLayout.addLayout(self.current_note_layout)
        self.masterLayout.addWidget(self.attachments_widget)
        # self.masterLayout.addSpacing(10)
        self.masterLayout.addLayout(self.children_layout)
        self.masterLayout.addLayout(self.reply_layout)
        self.masterLayout.addStretch()
        self.setLayout(self.masterLayout)

        self.reply_button.clicked.connect(self.reply_button_clicked)

    def show_attachments(self):
        for attachment in self.attachments:
            file_path = attachment.hosted_path
            # print file_path
            if os.path.exists(file_path):
                attachment_widget = AttachmentLabel(file_path, content_type=attachment.type)
                self.attachments_widget.add_widget(attachment_widget)

    def expand_children(self):
        for note in self.children:
            new_note_widget = ReplyWidget(note=note, text_color=self.text_color)
            self.children_layout.addWidget(new_note_widget)
        self.children_layout.addStretch()

    def add_reply_edit(self):
        self.reply_edit = AddNoteTextEdit(attachable=False)
        self.reply_layout.addWidget(self.reply_edit)
        self.reply_edit.cancelNote.connect(self.reply_edit_cancel)
        self.reply_edit.applyNote.connect(self.add_reply)

    def reply_button_clicked(self):
        if self.reply_edit is None:
            self.add_reply_edit()
        if not self.reply_edit.isVisible():
            self.reply_edit.setVisible(True)
            self.reply_edit.set_editable(True)
            version_notes_widget = self.parent().parent().parent()
            version_notes_widget.view_widget(self.reply_edit)

    def reply_edit_cancel(self):
        self.reply_edit.deleteLater()
        self.reply_edit = None

    def add_reply(self, content):
        if not isinstance(content, basestring):
            content = str(content.toUtf8())
        self.reply_edit.setVisible(False)
        new_reply = Reply.get(id=self.note_object.add_reply(content, self.current_user))
        new_note_widget = ReplyWidget(note=new_reply, text_color=self.text_color)
        self.children_layout.addWidget(new_note_widget)
        version_notes_widget = self.parent().parent().parent()
        version_notes_widget.view_widget(self.reply_edit)
        # print content

    def enterEvent(self, event):
        super(NoteWidget, self).enterEvent(event)
        self.reply_button.setVisible(True)

    def leaveEvent(self, event):
        super(NoteWidget, self).leaveEvent(event)
        self.reply_button.setVisible(False)

    def resizeEvent(self, event):
        super(NoteWidget, self).resizeEvent(event)
        if self.reply_edit is not None:
            self.reply_edit.setFixedWidth(self.width() * 0.7)
        self.reply_button.move(self.width() - self.reply_button.width(), 0)


class VersionInfoWidget(QtWidgets.QWidget):
    def __init__(self, text_color=None, *args, **kwargs):
        super(VersionInfoWidget, self).__init__(*args, **kwargs)

        self.text_color = QtWidgets.QApplication.palette().text().color() if text_color is None else text_color

        self.init_ui()

    def init_ui(self):

        self.version_submit_info_layout = QtWidgets.QHBoxLayout()

        self.user_icon_layout = QtWidgets.QVBoxLayout()
        self.user_icon = UserIconLabel()
        self.user_icon_layout.setAlignment(QtCore.Qt.AlignTop)
        self.user_icon_layout.addWidget(self.user_icon)

        self.version_layout = QtWidgets.QVBoxLayout()
        self.version_layout.setAlignment(QtCore.Qt.AlignTop)
        self.version_layout.setSpacing(0)
        self.user_time_layout = QtWidgets.QHBoxLayout()
        self.user_time_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.user_label = QtWidgets.QLabel()
        self.user_time_layout.addWidget(self.user_label)
        self.user_time_layout.addSpacing(15)
        self.user_time_label = QtWidgets.QLabel()
        self.user_time_label.setStyleSheet('color: rgb({}, {}, {}, 125)'.format(self.text_color.red(),
                                                                           self.text_color.green(),
                                                                           self.text_color.blue(), ))
        self.user_time_layout.addWidget(self.user_time_label)
        self.version_description_edit = AutoResizeTextEdit()
        self.version_layout.addLayout(self.user_time_layout)
        self.version_layout.addWidget(self.version_description_edit)
        # self.version_layout.addStretch()
        self.version_submit_info_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.version_submit_info_layout.setContentsMargins(4, 0, 0, 0)
        self.version_submit_info_layout.addLayout(self.user_icon_layout)
        self.version_submit_info_layout.addLayout(self.version_layout)

        self.setLayout(self.version_submit_info_layout)

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                 QtWidgets.QSizePolicy.Maximum))

        self.user_label.linkActivated.connect(self.open_link)

    def set_version(self, version=None):
        self.version_object = version

        self.version_user = self.version_object.artist
        self.version_date = self.version_object.date_created + TIME_DELTA
        self.version_description = self.version_object.description

        self.version_user_name = self.version_user.name
        self.user_icon.set_user(self.version_user)

        link_color_red, link_color_green, link_color_blue = get_link_color(self.text_color)
        self.user_label.setText("""
        <a href="{url}"><font color=#{color}>Version</font></a> by {version_user}
        """.format(url=self.version_object.url,
                   color='%02x%02x%02x' % (link_color_red,
                                           link_color_green,
                                           link_color_blue),
                   version_user=self.version_user_name,
                   ))
        self.user_time_label.setText(self.version_date.strftime('%Y-%m-%d %H:%M:%S'))
        self.version_description_edit.setText(self.version_description)
        self.version_description_edit.set_size()

    def open_link(self, url):
        webbrowser.open(str(url))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    note = Note.get(id=164253)
    window = NoteWidget(note=note, attachments=note.attachments)
    window.show()
    window.resize(500, 400)
    sys.exit(app.exec_())
