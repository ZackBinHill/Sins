# -*- coding: utf-8 -*-

import sys
import time
import getpass
import os
from BQt import QtWidgets, QtCore
from bfx.data.util.peewee import prefetch
from bfx.ui.component.toast import ToastWidget
from bfx.util.log import log_time_cost
from bfx.data.prod.shotgun.production2.models import Person, Version, Note, Reply, Attachment
from bfx.data.prod.shotgun.config import shotgun_api, SCRIPT_PLE
from bfx.data.ple.assets import AssetBase
from note_widgets import NoteWidget, ReplyWidget, UserIconLabel, AddNoteTextEdit, VersionInfoWidget


def add_new_note(version, subject='subject', content='', user=None):
    with shotgun_api(SCRIPT_PLE):
        version.add_note(subject=subject,
                         content=content,
                         note_type=None,
                         user=user,
                         status=None,
                         sg_type=None)
        new_note = (version.notes.select()
                    .order_by(Note.date_created.desc())
                    )[0]
        return new_note


class VersionNotesCenterWidget(QtWidgets.QWidget):
    def __init__(self, text_color=None, show_version=False, *args, **kwargs):
        super(VersionNotesCenterWidget, self).__init__(*args, **kwargs)

        self.setObjectName('VersionNotesCenterWidget')
        self.show_version = show_version
        self.text_color = QtWidgets.QApplication.palette().text().color() if text_color is None else text_color

        self.current_user = Person.get(login=getpass.getuser())

        self.init_ui()

        self.upload_thread = UploadThread()
        self.upload_thread.loadFinish.connect(self.refresh_after_add)

    def init_ui(self):

        self.version_info_widget = VersionInfoWidget(text_color=self.text_color)
        if self.show_version:
            self.version_info_widget.show()
        else:
            self.version_info_widget.hide()

        self.notes_layout = QtWidgets.QVBoxLayout()
        self.notes_layout.setAlignment(QtCore.Qt.AlignTop)
        self.notes_layout.setContentsMargins(0, 0, 0, 0)

        self.add_note_layout = QtWidgets.QHBoxLayout()

        self.user_icon_layout = QtWidgets.QVBoxLayout()
        self.user_icon = UserIconLabel()
        self.user_icon.set_user(self.current_user)
        self.user_icon_layout.setAlignment(QtCore.Qt.AlignTop)
        self.user_icon_layout.addWidget(self.user_icon)

        self.add_note_edit = AddNoteTextEdit()
        self.add_note_layout.addLayout(self.user_icon_layout)
        self.add_note_layout.addSpacing(8)
        self.add_note_layout.addWidget(self.add_note_edit)
        self.add_note_layout.addStretch()
        self.add_note_layout.setContentsMargins(3, 0, 0, 0)

        self.unsupport_label = QtWidgets.QLabel('unsupported version!')
        self.unsupport_label.setAlignment(QtCore.Qt.AlignCenter)
        self.unsupport_label.setVisible(False)
        self.unsupport_label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                                                 QtWidgets.QSizePolicy.MinimumExpanding))

        self.show_all_notes_button = QtWidgets.QPushButton('Show All Notes')
        self.show_all_notes_button.clicked.connect(self.show_all_notes)
        self.show_all_notes_button.setStyleSheet("""
        QPushButton{
            background:transparent;
            border:none;
            color: rgb(%s, %s, %s, 100);
        }
        QPushButton:hover{
            color: rgb(%s, %s, %s, 150);
        }
        
        """ % (self.text_color.red(),
               self.text_color.green(),
               self.text_color.blue(),
               self.text_color.red(),
               self.text_color.green(),
               self.text_color.blue(),
               ))
        self.show_all_notes_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.show_all_notes_button.hide()

        self.masterLayout = QtWidgets.QVBoxLayout()
        self.masterLayout.setAlignment(QtCore.Qt.AlignTop)
        self.masterLayout.addWidget(self.version_info_widget)
        self.masterLayout.addWidget(self.show_all_notes_button)
        self.masterLayout.addLayout(self.notes_layout)
        self.masterLayout.addLayout(self.add_note_layout)
        self.masterLayout.addWidget(self.unsupport_label)
        self.masterLayout.addStretch()
        self.setLayout(self.masterLayout)

        self.user_icon.hide()
        self.add_note_edit.hide()

        self.add_note_edit.applyNote.connect(self.add_new_note)

    def set_add_note_widget_visible(self, visible=True):
        if visible:
            self.user_icon.show()
            self.add_note_edit.show()
        else:
            self.user_icon.hide()
            self.add_note_edit.hide()

    def clear_notes(self):
        for index in reversed(range(self.notes_layout.count())):
            widget = self.notes_layout.itemAt(index).widget()
            widget.setParent(None)
            self.notes_layout.removeWidget(widget)

    @log_time_cost
    def add_notes(self, max_count=2):
        notes_count = self.notes.count()
        for index, note in enumerate(self.notes):
            if notes_count - index <= max_count:
                self.insert_note(note, index)
        self.hided_notes_count = notes_count - max_count
        if self.hided_notes_count <= 0:
            self.show_all_notes_button.hide()
        else:
            self.show_all_notes_button.show()

    def show_all_notes(self):
        for index, note in enumerate(self.notes[:self.hided_notes_count]):
            self.insert_note(note, index)
        self.hided_notes_count = 0
        self.show_all_notes_button.hide()

    def insert_note(self, note, index=0):
        note_widget = NoteWidget(note=note,
                                 current_user=self.current_user,
                                 attachments=[n.attachments for n in self.notes_with_attachment if n.id == note.id],
                                 text_color=self.text_color
                                 )
        self.notes_layout.insertWidget(index, note_widget)
        QtCore.QCoreApplication.processEvents()

    @log_time_cost
    def set_version(self, version=None):
        self.clear_notes()
        if hasattr(version, 'shotgun_host') and version.shotgun_host != 'shotgun2.base-fx.com':
            self.unsupport_label.setVisible(True)
            self.unsupport_label.setText('not supported to read notes from {}'.format(version.shotgun_host))
            self.set_add_note_widget_visible(False)
        elif isinstance(version, AssetBase):
            self.unsupport_label.setVisible(True)
            self.unsupport_label.setText('not supported to read notes from ple version')
            self.set_add_note_widget_visible(False)
        else:
            self.version_object = None
            if isinstance(version, (basestring, int)):
                try:
                    self.version_object = Version.get(id=version)
                except Version.DoesNotExist:
                    pass
            else:
                self.version_object = version

            if self.version_object is not None:
                self.unsupport_label.hide()
                self.set_add_note_widget_visible(True)
                if not self.version_info_widget.isHidden():
                    self.version_info_widget.set_version(self.version_object)

                self.notes = (self.version_object.notes
                              .order_by(Note.date_created))
                self.notes = prefetch(self.notes, Person)
                self.notes = prefetch(self.notes, (Reply, Note), Person)
                self.notes_with_attachment = (Note
                         .select(Note, Attachment)
                         .join(Attachment, on=(Attachment.entity_type == 'Note') & (Attachment.entity_id == Note.id))
                         .where(Note.id.in_(self.version_object.notes)))

                # print type(self.notes)
                # self.clear_notes()
                self.add_notes()
            else:
                self.set_add_note_widget_visible(False)

    def add_new_note(self, content):
        subject = '{}\'s note on {}'.format(self.current_user.firstname, self.version_object.name)
        if not isinstance(content, basestring):
            content = str(content.toUtf8())
        # print content, type(content), u'{content}'.format(content=content)
        self.new_note = add_new_note(self.version_object, subject=subject, content=content, user=self.current_user)

        if len(self.add_note_edit.attach_files) != 0:
            self.upload_thread.set_files(self.new_note, self.add_note_edit.attach_files)
            self.upload_thread.start()
        else:
            self.refresh_after_add()

    def refresh_after_add(self):
        note_widget = NoteWidget(current_user=self.current_user,
                                 note=self.new_note,
                                 parent=self,
                                 attachments=self.new_note.attachments)
        self.notes_layout.addWidget(note_widget)
        # self.parent().parent().view_bottom()
        self.parent().parent().view_widget(self.add_note_edit)
        toast = ToastWidget(parent=self.parent().parent())
        toast.showText('Create a new note on version {}'.format(self.version_object.name))

    def resizeEvent(self, event):
        super(VersionNotesCenterWidget, self).resizeEvent(event)
        self.add_note_edit.setFixedWidth(self.width() * 0.7)


class UploadThread(QtCore.QThread):
    loadFinish = QtCore.pyqtSignal()

    def __init__(self):
        super(UploadThread, self).__init__()

    def set_files(self, new_note, attach_files):

        self.new_note = new_note
        self.attach_files = attach_files

    def run(self):
        for attach_file in self.attach_files:
            self.new_note.upload_reference_file(attach_file)
        self.loadFinish.emit()


class VersionNotesWidget(QtWidgets.QScrollArea):
    testSignal = QtCore.pyqtSignal(int)

    def __init__(self, text_color=None, show_version=False, parent=None):
        super(VersionNotesWidget, self).__init__(parent)

        self.setStyleSheet("""
        QScrollArea{
            border:none;
        }
        QTextEdit{
            border:none;
            background:transparent;
        }
        QLabel{
            background:transparent;
        }
        QPushButton{
            background:transparent;
            padding:0px;
            margin:0px;
        }
        """)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.text_color = QtWidgets.QApplication.palette().text().color() if text_color is None else text_color

        self.versionNotesCenterWidget = VersionNotesCenterWidget(text_color=self.text_color,
                                                                 show_version=show_version)
        self.versionNotesCenterWidget.add_note_edit.changed.connect(self.add_note_edit_changed)
        self.setWidget(self.versionNotesCenterWidget)
        # print self.versionNotesCenterWidget.parent().objectName()
        self.versionNotesCenterWidget.parent().setStyleSheet("""
        QWidget{
            background:transparent;
        }
        """)
        self.setWidgetResizable(True)

    def add_note_edit_changed(self):
        self.view_bottom()

    def view_bottom(self):
        # print 'view bottom'
        # self.takeWidget()
        self.setWidget(self.versionNotesCenterWidget)
        self.versionNotesCenterWidget.adjustSize()
        vertical_scroll_bar = self.verticalScrollBar()
        vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())

    def view_widget(self, widget):
        if isinstance(widget, NoteWidget):
            y = widget.pos().y()
        elif isinstance(widget, (AddNoteTextEdit, ReplyWidget)) and isinstance(widget.parent(), NoteWidget):
            # print widget.parent(), widget.pos(), widget.parent().pos()
            # print widget.mapTo(self, widget.pos()), widget.mapToParent(widget.pos())
            y = widget.pos().y() + widget.parent().pos().y()
        else:
            y = widget.pos().y()
        y = y - (self.height() - widget.height()) / 2
        # print y
        vertical_scroll_bar = self.verticalScrollBar()
        vertical_scroll_bar.setValue(y)

    def set_version(self, version):
        self.versionNotesCenterWidget.set_version(version=version)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = VersionNotesWidget(show_version=True)
    window.show()
    a = time.time()
    # window.set_version(version=103675)
    window.set_version(version=105045)  # xtst
    # window.set_version(Version.get(id=12345))
    # window.set_version(version=105363)
    # window.set_version(version=105735)
    # window.set_version(version=106391)  # attachment
    window.resize(500, 400)
    print time.time() - a
    sys.exit(app.exec_())
