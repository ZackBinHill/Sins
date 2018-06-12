# -*- coding: utf-8 -*-
from BQt import QtWidgets, QtGui, QtCore
import sys
from view import GraphicsView


class GraphicsSceneWidget(QtWidgets.QWidget):
    """Display the node graph and offer editing functionality."""

    itemDoubleClicked = QtCore.pyqtSignal(object)

    def __init__(self, combine_version=False, parent=None):
        super(GraphicsSceneWidget, self).__init__(parent=parent)

        self.scene = GraphicsScene(combine_version=combine_version, parent=self)
        # orientation: 0-h 1-v
        self.view = GraphicsView()
        self.view.setScene(self.scene)
        self.setGeometry(100, 100, 800, 600)

        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setViewportUpdateMode(
            QtWidgets.QGraphicsView.FullViewportUpdate)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.scene.setSceneRect(QtCore.QRectF(-(self.view.viewport().width() / self.view.current_zoom * 2 + 25000) / 2,
                                              -(self.view.viewport().height() / self.view.current_zoom * 2 + 25000) / 2,
                                              self.view.viewport().width() / self.view.current_zoom * 2 + 25000,
                                              self.view.viewport().height() / self.view.current_zoom * 2 + 25000))

    def set_root_version_item(self, version_item, populate_layer):
        self.scene.clear()
        self.scene.addItem(version_item)

        version_item.setPos(0, 0)
        version_item.show_version_widget()
        version_item.populate_children(populate_layer, reset_pos=True)

        self.view.fit_to(self.scene.selectedItems())


class GraphicsScene(QtWidgets.QGraphicsScene):

    def __init__(self, combine_version=False, **kwargs):
        super(GraphicsScene, self).__init__(**kwargs)

        self.combine_version = combine_version

        self.depth = 0

        self.max_y_depth = 0

        self.node_dict = {
            "depth": 2,
            "nodes": {}
        }

        self.setSceneRect(QtCore.QRectF(-25000 / 2, -25000 / 2, 25000, 25000))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GraphicsSceneWidget()
    window.show()
    sys.exit(app.exec_())
