# -*- coding: utf-8 -*-
import os
# os.environ['BFX_LOG'] = 'debug'
import sys
from BQt import QtWidgets, uic, QtCore

from bfx.ui.version_graph.node_graph.graph_widget import GraphicsSceneWidget
from bfx.ui.version_graph.node_graph.node import VersionItem
from bfx.util.log import bfx_get_logger
from bfx.ui import get_icon
from bfx_resources.icons import ICON_DIR

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

    def set_orientation(self, value):
        self.orientation = value

    def set_populate_depth(self, value):
        self.default_populate_depth = value

    def init_ui(self):
        self.checkSelectedButton = QtWidgets.QPushButton()
        self.checkSelectedButton.setToolTip('Check newest of select version')
        self.checkSelectedButton.setIcon(
            get_icon(os.path.join(ICON_DIR, 'action', 'svg', 'ic_find_replace_48px.svg'), color='white'))
        self.checkSelectedButton.setIconSize(QtCore.QSize(25, 25))

        self.checkAllButton = QtWidgets.QPushButton()
        self.checkAllButton.setToolTip('Check newest of all version')
        self.checkAllButton.setIcon(
            get_icon(os.path.join(ICON_DIR, 'action', 'svg', 'ic_autorenew_48px.svg'), color='white'))
        self.checkAllButton.setIconSize(QtCore.QSize(25, 25))

        self.expandAllButton = QtWidgets.QPushButton()
        self.expandAllButton.setToolTip('Expand all versions')
        self.expandAllButton.setIcon(
            get_icon(os.path.join(ICON_DIR, 'action', 'svg', 'ic_swap_horiz_24px.svg'), color='white'))
        self.expandAllButton.setIconSize(QtCore.QSize(25, 25))

        for button in [self.checkSelectedButton, self.checkAllButton, self.expandAllButton]:
            button.setFixedSize(25, 25)

        self.horizontalLayout.addWidget(self.checkSelectedButton)
        self.horizontalLayout.addWidget(self.checkAllButton)
        self.horizontalLayout.addWidget(self.expandAllButton)

        self.scene_widget = GraphicsSceneWidget(combine_version=self.combine_version,
                                                parent=self)
        self.scene_widget.itemDoubleClicked.connect(self.__item_double_clicked)
        self.view_layout.addWidget(self.scene_widget)

        self.setStyleSheet("""
        *{
            color:white;
            background-color:rgb(50, 50, 50);
            border:none
        }
        QPushButton:hover{
            background-color:rgb(60, 60, 60);
        }
        QPushButton:pressed{
            background-color:rgb(40, 40, 40);
        }
        QLabel{
            background-color:transparent;
        }
        """)

        self.checkSelectedButton.clicked.connect(self.scene_widget.check_selected_version)
        self.checkAllButton.clicked.connect(self.scene_widget.check_all_version)
        self.expandAllButton.clicked.connect(self.scene_widget.expand_all)

    def show_version(self, version):
        if self.root_version_item and self.root_version_item.version.id == version.id:
            return

        exporter = version.get_exporter()
        self.version_name_label.setText("{} ({})".format(version.name,
                                                         exporter.basset_url.asset.name))
        self.version_info_label.setText(exporter.basset_url.entity.get_full_name())

        self.root_version_item = VersionItem.create_item(version)
        self.root_version_item.set_color(self.root_version_item.entity.name)
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
        self.version_item_double_clicked.emit(item)


def main():
    """main function that's render when the script is render as a standalone script."""
    app = QtWidgets.QApplication(sys.argv)
    from bfx.data.ple.assets import Version
    # v = Version.get(id=834342)
    # v = Version.get(id=818022)
    # v = Version.get(id=606882)  # cc_bundle
    # v = Version.get(id=579564)
    # v = Version.get(id=659547)
    v = Version.get(id=898056)
    window = VersionGraph(combine_version=True)
    window.set_populate_depth(1)
    window.set_orientation(0)
    window.show()
    window.show_version(v)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
