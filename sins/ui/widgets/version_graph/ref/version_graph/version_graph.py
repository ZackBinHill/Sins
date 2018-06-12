# -*- coding: utf-8 -*-
import os
import sys
from BQt import QtWidgets, uic, QtCore

from bfx.ui.version_graph.node_graph.graph_widget import GraphicsSceneWidget
from bfx.ui.version_graph.node_graph.node import VersionItem
from bfx.util.log import bfx_get_logger

logger = bfx_get_logger(__name__)
logger.debug("loading module {0} at {1}".format(__name__, __file__))


class VersionGraph(QtWidgets.QWidget):
    version_item_double_clicked = QtCore.pyqtSignal(object)

    def __init__(self, populate_depth=3, combine_version=False, orientation=0, parent=None):
        super(VersionGraph, self).__init__(parent=parent)

        # setup UI -------------------------------------------- #
        ui_file = os.path.join(os.path.dirname(__file__), 'design', 'main.ui')
        uic.loadUi(ui_file, self)

        self.root_version_item = None
        self.default_populate_depth = populate_depth
        self.combine_version = combine_version
        self.orientation = orientation

        self.init_ui()

    def set_populate_depth(self, value):
        self.default_populate_depth = value

    def init_ui(self):
        self.scene_widget = GraphicsSceneWidget(combine_version=self.combine_version,
                                                parent=self)
        self.scene_widget.itemDoubleClicked.connect(self.__item_double_clicked)
        self.view_layout.addWidget(self.scene_widget)

        self.setStyleSheet("color:white;"
                           "background-color:rgb(50, 50, 50);"
                           "border:none")

    def show_version(self, version):
        if self.root_version_item and self.root_version_item.version.id == version.id:
            return

        exporter = version.get_exporter()
        self.version_name_label.setText("{} ({})".format(version.name,
                                                         exporter.basset_url.asset.name))
        self.version_info_label.setText(exporter.basset_url.entity.get_full_name())

        self.root_version_item = VersionItem.create_item(version)
        self.root_version_item.set_orientation(self.orientation)
        self.scene_widget.set_root_version_item(self.root_version_item, self.default_populate_depth)

    def keyPressEvent(self, event):
        super(VersionGraph, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Space:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

    def __item_double_clicked(self, item):
        print item
        self.version_item_double_clicked.emit(item)


def main():
    """main function that's render when the script is render as a standalone script."""
    app = QtWidgets.QApplication(sys.argv)
    from bfx.data.ple.assets import Version
    v = Version.get(id=818022)
    # v = Version.get(id=606882)  # cc_bundle
    # v = Version.get(id=579564)
    # v = Version.get(id=659547)
    window = VersionGraph(combine_version=True, orientation=0)
    window.set_populate_depth(10)
    window.show()
    window.show_version(v)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()