# -*- coding: utf-8 -*-

"""Tag classes."""

from BQt import QtWidgets, QtGui, QtCore
import os
from bfx_resources.icons import ICON_DIR
from bfx.ui import get_pixmap


TAG_SHAPES = [
    '',
    'Rect',
    'Ellipse',
    'Triangle0',
    'Triangle2',
]
TAG_W = 25
TAG_H = 25


def get_rect_of_ellipse(center_x, center_y, radius):
    x = center_x - radius
    y = center_y - radius
    w = 2.0 * radius
    h = 2.0 * radius
    return QtCore.QRectF(x, y, w, h)


def get_shapes_of_triangle(a, roundness=0, direction=0):
    points = [
        QtCore.QPointF(1.732 * roundness, a),
        QtCore.QPointF(1.732 / 2 * roundness, a - 1.5 * roundness),
        QtCore.QPointF(0.5 * a - 1.732 / 2 * roundness, 1.5 * roundness),
        QtCore.QPointF(0.5 * a + 1.732 / 2 * roundness, 1.5 * roundness),
        QtCore.QPointF(a - 1.732 / 2 * roundness, a - 1.5 * roundness),
        QtCore.QPointF(a - 1.732 * roundness, a),
    ]
    centers = [
        QtCore.QPointF(0.5 * a, 2.0 * roundness),
        QtCore.QPointF(1.732 * roundness, a - roundness),
        QtCore.QPointF(a - 1.732 * roundness, a - roundness),
    ]
    if direction == 0:
        points = [point - QtCore.QPointF(0, 1.732 / 4 * roundness) for point in points]
        centers = [point - QtCore.QPointF(0, 1.732 / 4 * roundness) for point in centers]
    elif direction == 2:
        points = [QtCore.QPointF(point.x(), -1 * point.y() + a + 1.732 / 4 * roundness) for point in points]
        centers = [QtCore.QPointF(point.x(), -1 * point.y() + a + 1.732 / 4 * roundness) for point in centers]
    rects = [get_rect_of_ellipse(center.x(), center.y(), roundness) for center in centers]
    return points, rects


class Tag(QtWidgets.QGraphicsItem):
    """A Tag is a socket of a Node and can be connected to other Tags."""

    def __init__(self, shape=None, text=None, color=None, **kwargs):
        super(Tag, self).__init__(**kwargs)

        self.shape = shape
        self.text = text
        self.color = color

        self.x = 0
        self.y = 0
        self.w = TAG_W
        self.h = TAG_H

        self.margin = 5

        self.name = "value"
        self.displayName = self.name
        self.auto_hide = True

        self.textColor = QtGui.QColor(10, 10, 10)
        self.fillColor = self.color if self.color is not None else QtGui.QColor(170, 170, 170)
        self.highlightColor = QtGui.QColor(255, 255, 0)

        self.setAcceptHoverEvents(True)

    def node(self):
        """The Node that this Tag belongs to is its parent item."""
        return self.parentItem()

    def boundingRect(self):
        """Return the bounding box of this Tag."""
        rect = QtCore.QRectF(self.x,
                             self.y,
                             self.w,
                             self.h)
        return rect

    def paint(self, painter, option, widget):
        """Draw the Tag's shape and label."""
        bbox = self.boundingRect()

        if self.shape is not None:
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            painter.setBrush(QtGui.QBrush(self.fillColor))

            # Draw a filled rectangle.
            if self.shape == 1:
                roundness = 3
                painter.drawRoundedRect(bbox, roundness, roundness)

            # Ellipse
            if self.shape == 2:
                painter.drawEllipse(bbox)

            # Triangle0
            if self.shape == 3:
                points, rects = get_shapes_of_triangle(self.w, roundness=2, direction=0)
                painter.drawPolygon(QtGui.QPolygonF(points))
                for rect in rects:
                    painter.drawEllipse(rect)

            # Triangle2
            if self.shape == 4:
                points, rects = get_shapes_of_triangle(self.w, roundness=2, direction=2)
                painter.drawPolygon(QtGui.QPolygonF(points))
                for rect in rects:
                    painter.drawEllipse(rect)

        if self.text is not None:
            painter.setPen(QtGui.QPen(self.textColor))
            font = painter.font()
            fm = QtGui.QFontMetrics(font)
            w = fm.boundingRect(self.text).width() + 10
            h = fm.boundingRect(self.text).height()
            rect = QtCore.QRectF(0 - (w - bbox.width()) / 2.0,
                                 0 - (h - bbox.height()) / 2.0,
                                 w,
                                 h)
            painter.drawText(rect, QtCore.Qt.AlignCenter, self.text)


class PixmapTag(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, icon=None, **kwargs):
        super(PixmapTag, self).__init__(**kwargs)

        self.scale_factor = 10
        self.w = TAG_W
        self.h = TAG_H
        self.icon = icon

        self.auto_hide = True
        self.setAcceptHoverEvents(True)

    def set_pixmap(self, color=None):
        self.setPixmap(get_pixmap(self.icon,
                                  color=color,
                                  size=QtCore.QSize(TAG_W * self.scale_factor, TAG_H * self.scale_factor)))
        self.setScale(1.0 / self.scale_factor)


# class ColorTag(PixmapTag):
#     def __init__(self):
#         super(ColorTag, self).__init__()
#         self.icon = os.path.join(os.path.dirname(__file__), 'icons', 'color.png')
#         self.set_pixmap()
#         self.auto_hide = False


class WarningTag(PixmapTag):
    def __init__(self, warning=''):
        super(WarningTag, self).__init__()
        self.icon = os.path.join(ICON_DIR, 'alert', 'svg', 'ic_warning_48px.svg')
        self.setToolTip(warning)
        self.set_pixmap(color=[250, 20, 20])
        self.auto_hide = False
