# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/20/2018

import os
import sys
from sins.module.sqt import *
from sins.db.models import prefetch, File
from version_item import VersionItemWidget, VersionTreeItem


class VersionTree(QTreeWidget):
    currentVersionChanged = Signal(object)

    def __init__(self, *args, **kwargs):
        super(VersionTree, self).__init__(*args, **kwargs)

        self.init()

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.itemDoubleClicked.connect(self.item_double_clicked)

        button = QPushButton('test', self)
        button.clicked.connect(self.test1)

    def init(self):
        self.clear()
        self.current_version = None
        self.last_item = None
        self.all_version_items = []

    def set_entity(self, entity):
        versions = entity.versions
        for version in versions:
            print version.id
            version_item = VersionTreeItem(version, tree=self)
            self.addTopLevelItem(version_item)
            self.all_version_items.append(version_item)

            version_item_widget = VersionItemWidget(version)
            self.setItemWidget(version_item, 0, version_item_widget)

            version_item_widget.add_infos(['name', 'status_', 'type'])

    def set_current_version(self, version=None, current_version_item=None):
        if self.last_item != current_version_item or version is not None:
            if self.last_item is not None:
                self.last_item.set_current(False)

            if version is not None:
                for version_item in self.all_version_items:
                    if version_item.version == version:
                        current_version_item = version_item
                        break

            current_version_item.setSelected(True)
            current_version_item.set_current()
            self.last_item = current_version_item
            self.current_version = current_version_item.version

            self.currentVersionChanged.emit(self.current_version)

    def item_double_clicked(self, treeitem, p_int):
        version_item_widget = self.itemWidget(treeitem, 0)
        self.set_current_version(current_version_item=treeitem)

    def test(self):
        tree_item = self.topLevelItem(0)
        item_widget = self.itemWidget(tree_item, 0)
        item_widget.add_infos(['type'])
        tree_item.setSizeHint(0, QSize(100, item_widget.minimumHeight()))
        self.updateGeometries()

    def test1(self):
        from test_model import Version, Task
        task = Task.get(id=24432)
        self.init()
        self.set_entity(task)
        self.set_current_version(version=Version.get(id=77882))




if __name__ == '__main__':
    from test_model import Version, Task
    task = Task.get(id=24430)
    app = QApplication(sys.argv)
    window = VersionTree()
    window.show()
    window.resize(500, 400)
    window.set_entity(task)
    window.set_current_version(Version.get(id=87709))
    sys.exit(app.exec_())