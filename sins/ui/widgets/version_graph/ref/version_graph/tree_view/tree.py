# -*- coding: utf-8 -*-

import sys
import os

from BQt import QtWidgets, uic

from bfx.util.log import bfx_get_logger

logger = bfx_get_logger(__name__)
logger.debug("loading module {0} at {1}".format(__name__, __file__))


class TreeWidget(QtWidgets.QWidget):
    def __init__(self, version=None):
        super(TreeWidget, self).__init__()

        # setup UI -------------------------------------------- #
        ui_file = os.path.join(os.path.dirname(__file__), "..", 'design', 'tree.ui')
        uic.loadUi(ui_file, self)
        if not version:
            return
        self.dependency_versions = []
        self.version = version
        self.current_version = None
        self. init_ui()

    def tree_item(self, version):
        tree_item = []
        exporter = version.get_exporter()
        tree_item.append(version.name)
        tree_item.append(exporter.basset_url.asset.name)
        tree_item.append(exporter.basset_url.entity.get_full_name())
        return tree_item

    def dependency_version(self, version):
        dependency_versions = []
        for dep_source in version.sources:
            dependency_version = [self.tree_item(dep_source), dep_source]
            dependency_versions.append(dependency_version)
        return dependency_versions

    def init_ui(self):
        self.tree_widget_item = QtWidgets.QTreeWidgetItem(self.tree_item(self.version))
        d_versions = self.dependency_version(self.version)
        self.updat_ui(self.tree_widget_item, d_versions)
        self.tree_widget.addTopLevelItem(self.tree_widget_item)

    def updat_ui(self, version_item, d_versions):
        for d_version in d_versions:
            d_version_item = QtWidgets.QTreeWidgetItem(d_version[0])
            version_item.addChild(d_version_item)
            if d_version[1].sources:
                d_sources = self.dependency_version(d_version[1])
                self.updat_ui(d_version_item, d_sources)


def main():
    """main function that's render when the script is render as a standalone script."""
    app = QtWidgets.QApplication(sys.argv)
    from bfx.data.ple.assets import Version
    v = Version.get(id=128875)
    window = TreeWidget(v)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()