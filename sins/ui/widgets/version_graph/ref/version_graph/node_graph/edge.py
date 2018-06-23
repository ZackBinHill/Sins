# -*- coding: utf-8 -*-
from BQt import QtWidgets, QtGui, QtCore
import math


class Edge(QtWidgets.QGraphicsPathItem):
    """A connection between two versions"""

    def __init__(self, **kwargs):
        super(Edge, self).__init__(**kwargs)

        # self.line_color = QtGui.QColor(10, 10, 10)
        self.normal_color = QtGui.QColor(130, 130, 130)
        self.highlight_color = QtGui.QColor(250, 250, 100)
        self.line_color = self.normal_color
        self.thickness = 1.5
        self.point_at_length = 7

        self.source = None
        self.target = None

        self.source_pos = QtCore.QPointF(0, 0)
        self.target_pos = QtCore.QPointF(0, 0)

        self.curv1 = 0.5
        self.curv3 = 0.5

        self.curv2 = 0.0
        self.curv4 = 1.0

        self.setAcceptHoverEvents(True)

    def set_line_color(self, highlight=False):
        if highlight:
            self.line_color = self.highlight_color
        else:
            self.line_color = self.normal_color

    def update_path(self, orientation):
        if self.source:
            self.source_pos = self.source.mapToScene(self.source.boundingRect().center())

        if self.target:
            self.target_pos = self.target.mapToScene(self.target.boundingRect().center())

        path = QtGui.QPainterPath()
        path.moveTo(self.source_pos)

        dx = self.target_pos.x() - self.source_pos.x()
        dy = self.target_pos.y() - self.source_pos.y()
        if orientation in [0, 2]:
            if (dx < 0 and orientation == 0) or (dx >= 0 and orientation == 2):
                self.curv1 = -0.5
                self.curv3 = 1.5
                self.curv2 = 0.2
                self.curv4 = 0.8
            else:
                self.curv1 = 0.5
                self.curv3 = 0.5
                self.curv2 = 0.0
                self.curv4 = 1.0
        elif orientation in [1, 3]:
            if (dy < 0 and orientation == 1) or (dy >= 0 and orientation == 3):
                self.curv1 = 0.2
                self.curv3 = 0.8
                self.curv2 = -0.5
                self.curv4 = 1.5
            else:
                self.curv1 = 0.0
                self.curv3 = 1.0
                self.curv2 = 0.5
                self.curv4 = 0.5

        ctrl1 = QtCore.QPointF(self.source_pos.x() + dx * self.curv1,
                               self.source_pos.y() + dy * self.curv2)
        ctrl2 = QtCore.QPointF(self.source_pos.x() + dx * self.curv3,
                               self.source_pos.y() + dy * self.curv4)

        path.cubicTo(ctrl1, ctrl2, self.target_pos)
        self.setPath(path)

    def paint(self, painter, option, widget):
        zoom = self.scene().views()[0].current_zoom
        thickness = self.thickness / math.sqrt(zoom)
        point_at_length = self.point_at_length / math.sqrt(zoom)
        self.setPen(QtGui.QPen(self.line_color, thickness))
        self.setZValue(-1)
        super(Edge, self).paint(painter, option, widget)

        center_pos = self.path().pointAtPercent(0.5)
        center_angle = self.path().angleAtPercent(0.5)

        painter.translate(center_pos)
        painter.rotate(360 - (center_angle + 30))
        painter.drawLine(QtCore.QPointF(0, 0), QtCore.QPointF(point_at_length, 0))
        painter.rotate(60)
        painter.drawLine(QtCore.QPointF(0, 0), QtCore.QPointF(point_at_length, 0))


