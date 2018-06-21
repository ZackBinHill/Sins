# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/20/2018

import sys
from sins.module.sqt import *
from sins.db.models import prefetch, File


class VersionTree(QTreeWidget):
    def __init__(self, *args, **kwargs):
        super(VersionTree, self).__init__(*args, **kwargs)

    def set_entity(self, entity):
        print entity
        versions = entity.versions
        prefetch(versions, File)
        for version in versions:
            print version.id, version.name, version.uploaded_movie

    def set_current_version(self, version):
        print version



if __name__ == "__main__":
    from sins.db.models import Shot
    app = QApplication(sys.argv)
    panel = VersionTree()
    entity = Shot.get(id=31)
    panel.set_entity(entity)
    panel.show()
    app.exec_()


