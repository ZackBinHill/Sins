# -*- coding: utf-8 -*-
from BQt import QtWidgets, QtGui, QtCore
import sys
from view import GraphicsView
from node import VersionItem, ShowVersionWidgetEvent


class GraphicsSceneWidget(QtWidgets.QWidget):
    """Display the node graph and offer editing functionality."""

    itemDoubleClicked = QtCore.pyqtSignal(object)
    # itemPopulate = QtCore.pyqtSignal(int, object)
    showWidgetSignal = QtCore.pyqtSignal(int)

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

        # self.itemPopulate.connect(self.test, QtCore.Qt.QueuedConnection)
        self.showWidgetSignal.connect(self.show_version_widget, QtCore.Qt.QueuedConnection)

    def set_root_version_item(self, version_item, populate_layer):
        self.scene.clear()
        self.scene.addItem(version_item)

        version_item.setPos(0, 0)
        version_item.show_version_widget()
        version_item.populate_children(populate_layer, reset_pos=True)

        self.view.fit_to(self.scene.selectedItems())
        # self.showWidgetSignal.emit(0)

    def check_selected_version(self):
        for item in self.scene.selectedItems():
            item.check_new_version()

    def check_all_version(self):
        for item in self.scene.items():
            if isinstance(item, VersionItem):
                item.check_new_version()

    def expand_all(self):
        if len(self.scene.selectedItems()) == 0:
            for node in self.view.nodes():
                node.populate_children(populate_layer=100, reset_pos=True)
        else:
            for node in self.scene.selectedItems():
                if isinstance(node, VersionItem):
                    node.populate_children(populate_layer=100, reset_pos=True)

    def show_version_widget(self, index):
        if index < len(self.view.nodes()):
            node_item = self.view.nodes()[index]
            node_item.show_version_widget()
            self.showWidgetSignal.emit(index + 1)

    def event(self, event):
        # if event.type() == PopulateEvent.eventType:
        #     # print event.index, event.item
        #     if event.index < event.item.dependent_versions_count:
        #         event.item.populate_child(event.index)
        #         QtCore.QCoreApplication.postEvent(self, PopulateEvent(event.index + 1, event.item))
        #     return True
        if event.type() == ShowVersionWidgetEvent.eventType:
            event.item.show_version_widget()
            return True
        return super(GraphicsSceneWidget, self).event(event)


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
