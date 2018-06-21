# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/20/2018

import sys
from sins.module.sqt import *


class VersionItem(QWidget):
    def __init__(self, *args, **kwargs):
        super(VersionItem, self).__init__(*args, **kwargs)

    def set_version(self, version):
        print version




if __name__ == "__main__":
    from sins.db.models import Version
    app = QApplication(sys.argv)
    panel = VersionItem()
    version = Version.get(id=31)
    panel.set_version(version)
    panel.show()
    app.exec_()