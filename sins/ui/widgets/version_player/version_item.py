# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/20/2018

import os
import sys
from sins.module.sqt import *


THUMBNAIL_SIZE = [80, 45]


class VersionItemWidget(QWidget):
    def __init__(self, version=None, *args, **kwargs):
        super(VersionItemWidget, self).__init__(*args, **kwargs)

        self.version = version
        self.is_current_version = False

        self.init_ui()

        self.setCursor(Qt.PointingHandCursor)

    def init_ui(self):
        self.backLabel = QLabel(self)

        self.thumbnailLabel = QLabel('thumbnail')
        self.thumbnailLabel.setFixedSize(THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1])
        self.thumbnailLabel.setStyleSheet('background:gray')
        self.thumbnailLayout = QVBoxLayout()
        self.thumbnailLayout.addWidget(self.thumbnailLabel)
        self.thumbnailLayout.addStretch()

        self.infoLayout = QFormLayout()
        self.infoLayout.setSpacing(2)
        self.infoLayout.setLabelAlignment(Qt.AlignLeft)

        self.masterLayout = QHBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignTop)
        self.masterLayout.addLayout(self.thumbnailLayout)
        self.masterLayout.addLayout(self.infoLayout)
        self.setLayout(self.masterLayout)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Maximum))

    def set_version(self, version):
        self.version = version

    def add_infos(self, names):
        for name in names:
            label = QLabel()
            label.setText(getattr(self.version, name))
            setattr(label, 'is_celledit', True)
            self.infoLayout.addRow('%s ' % name, label)
        min_h = 0
        for i in range(self.infoLayout.count()):
            widget = self.infoLayout.itemAt(i).widget()
            if hasattr(widget, 'is_celledit') and widget.is_celledit:
                min_h += widget.sizeHint().height() + self.infoLayout.spacing()
        min_h += self.masterLayout.contentsMargins().top() + self.masterLayout.contentsMargins().bottom()

        self.setMinimumHeight(min_h)

    def set_background(self):
        if self.is_current_version:
            self.backLabel.setStyleSheet('background:rgb(40, 40, 40, 40)')
        else:
            self.backLabel.setStyleSheet('background:transparent')

    def resizeEvent(self, event):
        super(VersionItemWidget, self).resizeEvent(event)
        self.backLabel.setFixedSize(self.size())


class VersionTreeItem(QTreeWidgetItem):
    def __init__(self, version=None, tree=None, *args, **kwargs):
        super(VersionTreeItem, self).__init__(*args, **kwargs)

        self.version = version
        self.tree = tree

    def set_current(self, is_current=True):
        # print 'set current'
        version_item_widget = self.tree.itemWidget(self, 0)
        version_item_widget.is_current_version = is_current
        version_item_widget.set_background()



if __name__ == '__main__':
    from test_model import Version
    app = QApplication(sys.argv)
    window = VersionItemWidget(Version.get(id=89876))
    window.show()
    window.adjustSize()
    window.add_infos(['name', 'status_'])
    print window.minimumSizeHint()
    sys.exit(app.exec_())
