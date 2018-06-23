# -*- coding: utf-8 -*-

import sys
from BQt import QtGui
from BQt import QtCore
from BQt import QtWidgets
# from PyQt4 import QtOpenGL

from node import VersionItem, SPECIAL_COLOR
from edge import Edge
from knob import Knob
from bfx.ui.util import get_pipeline_color
from bfx.ui.const import PIPELINE_COLOR


ALTERNATE_MODE_KEY = QtCore.Qt.Key_Alt


class ColorLabel(QtWidgets.QLabel):
    def __init__(self, color, *args, **kwargs):
        super(ColorLabel, self).__init__(*args, **kwargs)
        self.setFixedSize(20, 20)
        if isinstance(color, list):
            if len(color) == 2 and isinstance(color[0], list):
                self.setStyleSheet("""
                    background:qlineargradient(spread:pad, 
                    x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgb({}, {}, {}), 
                    stop:1 rgb({}, {}, {}))
                """.format(color[0][0], color[0][1], color[0][2], color[1][0], color[1][1], color[1][2]))
            elif len(color) == 3:
                self.setStyleSheet('background:rgb({}, {}, {}, 200)'.format(color[0], color[1], color[2]))


class ColorTable(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ColorTable, self).__init__(parent)

        # self.setFixedWidth(110)
        self.masterLayout = QtWidgets.QVBoxLayout()

        self.showButton = QtWidgets.QPushButton('hide sheet', self)
        self.showButton.setStyleSheet("color:gray;text-align:right;border:none")

        self.colorLayout = QtWidgets.QFormLayout()
        keys = list(PIPELINE_COLOR._fields)
        keys.remove("other")
        keys.sort()
        # keys.append("other")
        for step in keys:
            color = get_pipeline_color(step)
            color_label = ColorLabel(color)
            self.colorLayout.addRow(step + '  ', color_label)
        for key in SPECIAL_COLOR:
            color = SPECIAL_COLOR[key]
            color_label = ColorLabel(color)
            self.colorLayout.addRow(key + '  ', color_label)
        self.colorLayout.addRow('other' + '  ', ColorLabel(get_pipeline_color('other')))

        self.colorGroup = QtWidgets.QGroupBox()
        self.colorGroup.setLayout(self.colorLayout)

        # self.masterLayout.addWidget(self.showButton)
        self.masterLayout.addSpacing(20)
        self.masterLayout.addWidget(self.colorGroup)

        self.setLayout(self.masterLayout)
        self.setStyleSheet("color:white;background:transparent")

        self.showButton.clicked.connect(self.show_btn_clicked)

    def show_color_sheet(self):
        self.colorGroup.show()
        self.showButton.setText('hide sheet')

    def hide_color_sheet(self):
        self.colorGroup.hide()
        self.showButton.setText('color sheet')

    def show_btn_clicked(self):
        if self.colorGroup.isHidden():
            self.show_color_sheet()
        else:
            self.hide_color_sheet()


class GraphicsView(QtWidgets.QGraphicsView):
    """This view will draw a grid in its background."""

    def __init__(self, *args, **kwargs):
        super(GraphicsView, self).__init__(*args, **kwargs)

        self.fillColor = QtGui.QColor(38, 38, 38)
        self.lineColor = QtGui.QColor(55, 55, 55)

        self.xStep = 20
        self.yStep = 20
        
        self.current_zoom = 1.0

        self.panningMult = 2.0 * self.current_zoom
        self.panning = False
        self.zoomStep = 1.1

        # Since we implement custom panning, we don't need the scrollbars.
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(self.SmartViewportUpdate)
        # self.glWidget = QtOpenGL.QGLWidget(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers))
        # self.glWidget.updateGL()
        # self.setViewport(self.glWidget)

        self.colorTable = ColorTable(self)
        # self.move_color_table()

    def nodes(self):
        """Return all Nodes in the scene."""
        return [i for i in self.scene().items() if isinstance(i, VersionItem)]

    def edges(self):
        """Return all Edges in the scene."""
        return [i for i in self.scene().items() if isinstance(i, Edge)]

    def redrawEdges(self):
        """Trigger a repaint of all Edges in the scene."""
        for edge in self.edges():
            edge.updatePath()

    def resize_scene(self):
        center_x = self.mapToScene(QtCore.QPoint(self.viewport().width() / 2, self.viewport().height() / 2)).x()
        center_y = self.mapToScene(QtCore.QPoint(self.viewport().width() / 2, self.viewport().height() / 2)).y()
        w = self.viewport().width() / self.current_zoom * 2 + 25000
        h = self.viewport().height() / self.current_zoom * 2 + 25000

        self.scene().setSceneRect(QtCore.QRectF(center_x - w / 2,
                                                center_y - h / 2,
                                                w,
                                                h))

        show_detail = True if self.current_zoom >= 0.5 else False
        point1 = self.mapToScene(QtCore.QPoint(0, 0))
        point2 = self.mapToScene(QtCore.QPoint(self.viewport().width(), self.viewport().height()))
        rect = QtCore.QRectF(point1, point2)
        for version_node in self.nodes():
            if hasattr(version_node, 'version_widget'):
                version_node.version_widget.setVisible(show_detail)
            else:
                if rect.contains(version_node.pos()) and show_detail:
                    # version_node.start_show_version_widget()
                    version_node.show_version_widget()
                    QtCore.QCoreApplication.processEvents()
            for knob in version_node.knobs():
                knob.setVisible(show_detail)
            for tag in version_node.tags():
                if tag.auto_hide:
                    tag.setVisible(show_detail)

    def keyPressEvent(self, event):
        """Trigger a redraw of Edges to update their color."""
        if event.key() == ALTERNATE_MODE_KEY:
            self.redrawEdges()
        super(GraphicsView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Trigger a redraw of Edges to update their color."""
        if event.key() == ALTERNATE_MODE_KEY:
            self.redrawEdges()
        super(GraphicsView, self).keyReleaseEvent(event)
        if event.text() == 'f':
            self.fit_to(self.scene().selectedItems())

    def fit_to(self, items=[]):
        if len(items) == 0:
            for item in self.scene().items():
                if isinstance(item, VersionItem):
                    items.append(item)

        max_x = items[0].pos().x()
        min_x = items[0].pos().x()
        max_y = items[0].pos().y()
        min_y = items[0].pos().y()
        for item in items:
            max_x = max(item.pos().x(), max_x)
            min_x = min(item.pos().x(), min_x)
            max_y = max(item.pos().y(), max_y)
            min_y = min(item.pos().y(), min_y)
        center_x = (max_x + min_x) / 2 + 100
        center_y = (max_y + min_y) / 2 + 40
        width = max_x - min_x
        height = max_y - min_y

        zoom_x = 1 / max(1, float(width + 1000) / self.viewport().width()) / self.current_zoom
        zoom_y = 1 / max(1, float(height + 1000) / self.viewport().height()) / self.current_zoom
        zoom = min(zoom_x, zoom_y)
        self.scale(zoom, zoom)
        self.current_zoom = self.transform().m11()
        self.resize_scene()

        self.centerOn(QtCore.QPointF(center_x, center_y))

    def mousePressEvent(self, event):
        """Initiate custom panning using middle mouse button."""
        selected_items = self.scene().selectedItems()
        if event.button() == QtCore.Qt.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.panning = True
            self.prevPos = event.pos()
            self.prev_center = self.mapToScene(QtCore.QPoint(self.viewport().width() / 2, self.viewport().height() / 2))
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        super(GraphicsView, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.MiddleButton:
            for item in selected_items:
                item.setSelected(True)
        self.highlight_connection()

    def mouseMoveEvent(self, event):
        if self.panning:
            mouse_move = event.pos() - self.prevPos
            newCenter = QtCore.QPointF(self.prev_center.x() - mouse_move.x() / self.current_zoom,
                                      self.prev_center.y() - mouse_move.y() / self.current_zoom)
            self.centerOn(newCenter)

            show_detail = True if self.current_zoom >= 0.5 else False
            if show_detail:
                point1 = self.mapToScene(QtCore.QPoint(0, 0))
                point2 = self.mapToScene(QtCore.QPoint(self.viewport().width(), self.viewport().height()))
                rect = QtCore.QRectF(point1, point2)
                for version_node in self.nodes():
                    if rect.contains(version_node.pos()) and not hasattr(version_node, 'version_widget'):
                        version_node.start_show_version_widget()
                        # print version_node.pos(), point1, point2

            return
        super(GraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.panning:
            self.panning = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(GraphicsView, self).mouseReleaseEvent(event)
        self.highlight_connection()

    def wheelEvent(self, event):
        positive = event.delta() >= 0
        zoom = self.zoomStep if positive else 1.0 / self.zoomStep
        self.scale(zoom, zoom)

        # Assuming we always scale x and y proportionally, expose the
        # current horizontal scaling factor so other items can use it.
        self.current_zoom = self.transform().m11()
        self.resize_scene()

    def move_color_table(self):
        # print self.width() - self.colorTable.width()
        self.colorTable.move(self.width() - self.colorTable.width() - 0, 0)

    def resizeEvent(self, event):
        super(GraphicsView, self).resizeEvent(event)
        self.move_color_table()

    def drawBackground(self, painter, rect):
        painter.setBrush(QtGui.QBrush(self.fillColor))
        painter.setPen(QtGui.QPen(self.lineColor))

        painter.drawRect(rect)
        lines = []
        scale = max(int(1 / self.current_zoom / 2), 1)
        line_w = 200 * scale
        line_h = 80 * scale

        point1 = self.mapToScene(QtCore.QPoint(0, 0))
        point2 = self.mapToScene(QtCore.QPoint(self.viewport().width(), self.viewport().height()))

        # for i in range(int(point1.y() / line_h), int(self.scene().height() / line_h)):
        for i in range(int(point1.y() / line_h), int(point2.y() / line_h)):
            lines.append(QtCore.QLineF(QtCore.QPoint(rect.x(), i * line_h),
                                      QtCore.QPoint(rect.x() + rect.width(), i * line_h)))
        # for i in range(int(self.scene().sceneRect().x()), int(self.scene().width() / line_w)):
        for i in range(int(point1.x() / line_w), int(point2.x() / line_w)):
            lines.append(QtCore.QLineF(QtCore.QPoint(i * line_w, rect.y()),
                                      QtCore.QPoint(i * line_w, rect.y() + rect.height())))
        painter.drawLines(lines)

        painter.setPen(QtGui.QPen(QtGui.QColor(80, 80, 60, 50)))
        painter.drawLine(QtCore.QLineF(QtCore.QPoint(rect.x(), 0), QtCore.QPoint(rect.x() + rect.width(), 0)))
        painter.drawLine(QtCore.QLineF(QtCore.QPoint(0, rect.y()), QtCore.QPoint(0, rect.y() + rect.height())))

    def highlight_connection(self):
        for item in self.scene().items():
            if isinstance(item, Knob):
                for edge in item.edges:
                    edge.set_line_color(highlight=False)
            if isinstance(item, VersionItem):
                version_exist = False
                for selected_item in self.scene().selectedItems():
                    if selected_item.id == item.id:
                        version_exist = True
                        break
                item.set_highlight(version_exist)
        for item in self.scene().selectedItems():
            for knob in item.knobs():
                for edge in knob.edges:
                    edge.set_line_color(highlight=True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GraphicsView()
    # window = ColorTable()
    window.show()
    sys.exit(app.exec_())