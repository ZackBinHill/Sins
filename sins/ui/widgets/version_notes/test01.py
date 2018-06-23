# -*- coding: utf-8 -*-

import sys
import time
import getpass
import os
# os.environ['BFX_LOG'] = 'debug'
# import webbrowser
from bfx.data.util.peewee import prefetch
from bfx.data.prod.shotgun.production2.models import *



# task = Task.get(id=28555)
# print task.notes
#
#
#
# person = Person.get(id=264)
# print person.image.hosted_path


# reply = Reply.get(id=1199)
# print reply.note
#
#
# note = Note.get(id=163051)
# for i in note.replies:
#     print i.content
#
#
# print '%02x' % 255
#
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
# from version_notes import VersionNotesWidget
# #
# #
# class Widget(QWidget):
#     def __init__(self):
#         super(Widget, self).__init__()
#         self.resize(500, 500)
#
#         widget1 = QLabel('aaaa')
#         self.widget2 = QLabel('bb')
#         self.widget2.setFixedHeight(50)
#         self.widget2.setStyleSheet('background:gray')
#         widget3 = QLabel('ccc')
#         self.layout1 = QVBoxLayout()
#         self.layout1.setAlignment(Qt.AlignTop)
#
#
#         self.masterlayout = QVBoxLayout()
#         self.masterlayout.setAlignment(Qt.AlignTop)
#         self.masterlayout.addWidget(widget1)
#         self.masterlayout.addLayout(self.layout1)
#         self.setLayout(self.masterlayout)
#
#     def test(self):
#         self.layout1.addWidget(self.widget2)
#
#
# class ScrollArea(QScrollArea):
#
#     def __init__(self):
#         super(ScrollArea, self).__init__()
#
#         self.setFrameShape(QFrame.NoFrame)
#
#         self.widget = Widget()
#         self.setWidget(self.widget)
#         self.setWidgetResizable(True)
#
#     def test(self):
#         self.widget.test()
#
#
#
# # from bfx.data.ple.assets import Version
# from bfx.data.prod.shotgun.production.models import Person, Version
# app = QApplication(sys.argv)
# # window = ScrollArea()
# window = VersionNotesWidget()
# window.show()
# window.set_version(Version.get(id=60682))
# sys.exit(app.exec_())

# note = Note.get(id=164078)
# for a in note.attachments:
#     print a

# a = Attachment.get(id=271379)
# print a.hosted_path
# print os.path.exists(a.hosted_path)


# version = Version(id=105045)
# notes = version.notes
# # notes = Note.select(Note, Attachment).join(Attachment, on=(Attachment.entity_type == 'Note') & (Attachment.entity_id == Note.id)).where(Note.id.in_(notes))
# notes = (Note
#          .select(Note, Attachment)
#          .join(Attachment, on=(Attachment.entity_type == 'Note') & (Attachment.entity_id == Note.id))
#          .where(Note.id.in_(notes)))
#
# for note in notes:
#     print 'note:', note.id
#     # for reply in note.replies:
#     #     print 'reply:', reply.id
#     print note.attachments.filename
#     # for attach in note.attachments:
#     #     print 'attach:', attach.id





# notes = (Note.select().join(Attachment)
#          .join(NoteLink)
#          .where((NoteLink.entity_id == 105045) & (NoteLink.entity_type == "Version")))
# print notes
# for note in notes:
#     print 'note:', note.id
#     # for reply in note.replies:
#     #     print 'reply:', reply.id
#     for attach in note.attachments:
#         print 'attach:', attach.id










# note = Note.get(id=164253)
# note.upload_reference_file('/local/workspace/test/out.mov')
# note.upload_reference_file('/local/workspace/test/test.py')





import webbrowser
webbrowser.open('/local/workspace/test/out.mov')







