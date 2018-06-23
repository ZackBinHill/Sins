# -*- coding: utf-8 -*-

import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
Signal = pyqtSignal
from version_tree import VersionTree


CURRENT_VERSION_THUMBNAIL_SIZE = [160, 90]


class CurrentVersion(QWidget):
    def __init__(self, *args, **kwargs):
        super(CurrentVersion, self).__init__(*args, **kwargs)

        self.init_ui()

    def init_ui(self):

        self.currentVersionLayout = QHBoxLayout()
        self.currentVersionThumb = QLabel('thumbnail')
        self.currentVersionThumb.setStyleSheet('background:gray')
        self.currentVersionThumb.setFixedSize(CURRENT_VERSION_THUMBNAIL_SIZE[0], CURRENT_VERSION_THUMBNAIL_SIZE[1])
        self.currentVersionName = QLabel()
        self.currentVersionLayout.addWidget(self.currentVersionThumb)
        self.currentVersionLayout.addWidget(self.currentVersionName)

        self.currentVersionInfoLayout = QFormLayout()

        self.masterLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.currentVersionLayout)
        self.masterLayout.addLayout(self.currentVersionInfoLayout)
        self.setLayout(self.masterLayout)

    def set_version(self, version):
        self.currentVersionName.setText(version.name)


class VersionBar(QWidget):
    def __init__(self, *args, **kwargs):
        super(VersionBar, self).__init__(*args, **kwargs)

        self.current_version = None

        self.init_ui()

        self.versionTree.currentVersionChanged.connect(self.current_version_changed)

    def init_ui(self):
        self.entityLabel = QLabel()
        self.entityLabel.setAlignment(Qt.AlignCenter)

        self.currentVersion = CurrentVersion()

        self.versionTree = VersionTree()

        self.mediaNotesTab = QTabWidget()
        self.mediaNotesTab.addTab(self.versionTree, 'Versions')
        self.mediaNotesTab.addTab(QLabel('notes'), 'Notes')

        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(self.entityLabel)
        self.masterLayout.addWidget(self.currentVersion)
        self.masterLayout.addWidget(self.mediaNotesTab)
        self.setLayout(self.masterLayout)

    def set_entity(self, entity):
        self.versionTree.set_entity(entity)
        self.entityLabel.setText(entity.name)

    def set_current_version(self, version):
        self.current_version = version
        self.versionTree.set_current_version(version)
        self.currentVersion.set_version(version)

    def current_version_changed(self, version):
        self.current_version = version
        self.currentVersion.set_version(version)





if __name__ == '__main__':
    from test_model import Version, Task
    task = Task.get(id=24430)
    app = QApplication(sys.argv)
    window = VersionBar()
    window.show()
    window.resize(500, 400)
    window.set_entity(task)
    window.set_current_version(Version.get(id=87709))
    sys.exit(app.exec_())


