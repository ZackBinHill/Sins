# -*- coding: utf-8 -*-

"""Knob classes."""

from BQt import QtWidgets, QtGui, QtCore

from edge import Edge

# Currently only affects Knob label placement.
FLOW_LEFT_TO_RIGHT = "flow_left_to_right"
FLOW_RIGHT_TO_LEFT = "flow_right_to_left"


class Knob(QtWidgets.QGraphicsItem):
    """A Knob is a socket of a Node and can be connected to other Knobs."""

    def __init__(self, **kwargs):
        kwargs.pop("name")

        super(Knob, self).__init__(**kwargs)
        self.x = 0
        self.y = 0
        self.w = 10
        self.h = 10

        self.margin = 5
        self.flow = FLOW_LEFT_TO_RIGHT

        self.maxConnections = -1  # A negative value means 'unlimited'.

        self.name = "value"
        self.displayName = self.name

        self.labelColor = QtGui.QColor(10, 10, 10)
        self.fillColor = QtGui.QColor(230, 230, 0)
        self.highlightColor = QtGui.QColor(255, 255, 0)

        # Temp store for Edge currently being created.
        self.newEdge = None

        self.edges = []

        self.setAcceptHoverEvents(True)

    def node(self):
        """The Node that this Knob belongs to is its parent item."""
        return self.parentItem()

    def connect_to(self, knob, orientation=0):
        """Convenience method to connect this to another Knob.

        This creates an Edge and directly connects it, in contrast to the mouse
        events that first create an Edge temporarily and only connect if the 
        user releases on a valid target Knob.
        """
        if knob is self:
            return

        edge = Edge()
        edge.source = self
        edge.target = knob

        self.add_edge(edge)
        knob.add_edge(edge)

        edge.update_path(orientation)

    def add_edge(self, edge):
        """Add the given Edge to the internal tracking list.

        This is only one part of the Knob connection procedure. It enables us to 
        later traverse the whole graph and to see how many connections there 
        currently are.

        Also make sure it is added to the QGraphicsScene, if not yet done.
        """
        self.edges.append(edge)
        scene = self.scene()
        if edge not in scene.items():
            scene.addItem(edge)

    def boundingRect(self):
        """Return the bounding box of this Knob."""
        rect = QtCore.QRectF(self.x,
                             self.y,
                             self.w,
                             self.h)
        return rect

    def highlight(self, toggle):
        """Toggle the highlight color on/off.

        Store the old color in a new attribute, so it can be restored.
        """
        if toggle:
            self._oldFillColor = self.fillColor
            self.fillColor = self.highlightColor
        else:
            self.fillColor = self._oldFillColor

    def paint(self, painter, option, widget):
        """Draw the Knob's shape and label."""
        bbox = self.boundingRect()

        # Draw a filled rectangle.
        # painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        pen = QtGui.QPen(QtGui.QColor(200, 200, 250))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(self.fillColor))
        # painter.drawRect(bbox)
        painter.drawEllipse(bbox)

        # Draw a text label next to it. Position depends on the flow.
        if self.flow == FLOW_LEFT_TO_RIGHT:
            x = bbox.right() + self.margin
        elif self.flow == FLOW_RIGHT_TO_LEFT:
            x = bbox.left() - self.margin
        else:
            raise Exception(
                "Flow not recognized: {0}".format(self.flow))
        y = bbox.bottom()
        self.setZValue(10)

        # painter.setPen(QtGui.QPen(self.labelColor))
        # painter.drawText(x, y, self.displayName)

    def destroy(self):
        """Remove this Knob, its Edges and associations."""
        print("destroy knob:", self)
        edges_to_delete = self.edges[::]  # Avoid shrinking during deletion.
        for edge in edges_to_delete:
            edge.destroy()
        node = self.parentItem()
        if node:
            node.removeKnob(self)

        self.scene().removeItem(self)
        del self


def ensure_edge_direction(edge):
    """Make sure the Edge direction is as described below.

       .source --> .target
    OutputKnob --> InputKnob

    Which basically translates to:

    'The Node with the OutputKnob is the child of the Node with the InputKnob.'

    This may seem the exact opposite way as expected, but makes sense
    when seen as a hierarchy: A Node which output depends on some other
    Node's input can be seen as a *child* of the other Node. We need
    that information to build a directed graph.

    We assume here that there always is an InputKnob and an OutputKnob
    in the given Edge, just their order may be wrong. Since the
    serialization relies on that order, it is enforced here.
    """
    print("ensure edge direction")
    if isinstance(edge.target, OutputKnob):
        assert isinstance(edge.source, InputKnob)
        actualTarget = edge.source
        edge.source = edge.target
        edge.target = actualTarget
    else:
        assert isinstance(edge.source, OutputKnob)
        assert isinstance(edge.target, InputKnob)

    print("src:", edge.source.__class__.__name__,
          "trg:", edge.target.__class__.__name__)


class InputKnob(Knob):
    """A Knob that represents an input value for its Node."""

    def __init__(self, *args, **kwargs):
        super(InputKnob, self).__init__(*args, **kwargs)
        self.name = kwargs.get("name", "input")
        self.displayName = kwargs.get("displayName", self.name)
        self.fillColor = kwargs.get("fillColor", QtGui.QColor(130, 230, 130))
        self.fillColor = kwargs.get("fillColor", QtGui.QColor(40, 60, 100))

    def finalize_edge(self, edge):
        ensure_edge_direction(edge)

    def hoverEnterEvent(self, event):
        super(InputKnob, self).hoverEnterEvent(event)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        event.accept()
        super(InputKnob, self).mouseReleaseEvent(event)

    def mouseReleaseEvent(self, event):
        super(InputKnob, self).mouseReleaseEvent(event)
        self.parentItem().populate_parent()


class OutputKnob(Knob):
    """A Knob that represents an output value for its Node."""

    def __init__(self, *args, **kwargs):
        super(OutputKnob, self).__init__(*args, **kwargs)
        self.name = kwargs.get("name", "output")
        self.displayName = kwargs.get("displayName", self.name)
        self.fillColor = kwargs.get("fillColor", QtGui.QColor(230, 130, 130))
        self.fillColor = kwargs.get("fillColor", QtGui.QColor(50, 100, 80))
        self.flow = kwargs.get("flow", FLOW_RIGHT_TO_LEFT)

    def finalize_edge(self, edge):
        ensure_edge_direction(edge)

    def hoverEnterEvent(self, event):
        super(OutputKnob, self).hoverEnterEvent(event)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        event.accept()
        super(OutputKnob, self).mouseReleaseEvent(event)

    def mouseReleaseEvent(self, event):
        super(OutputKnob, self).mouseReleaseEvent(event)
        self.parentItem().populate_children()


