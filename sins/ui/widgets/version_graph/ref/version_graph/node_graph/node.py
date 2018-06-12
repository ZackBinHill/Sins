# -*- coding: utf-8 -*-

from BQt import QtGui, QtCore, QtWidgets
from knob import InputKnob, OutputKnob, Knob
from tag import Tag, PixmapTag, ColorTag, WarningTag
from errors import DuplicateKnobNameError
from bfx.ui.version_graph.utils import open_version_in_browser, open_version_in_file_explorer
from bfx.ui.util import get_pipeline_color

TAG_MARGIN = 3


class Label(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)

    def paintEvent(self, qpaintevent):
        painter = QtGui.QPainter(self)
        font = painter.font()
        fm = QtGui.QFontMetrics(font)
        w = fm.boundingRect(self.text()).width() + 10
        h = fm.boundingRect(self.text()).height()
        painter.setFont(font)
        # painter.setPen(QtGui.QPen(QtGui.QColor(10, 10, 10)))
        painter.drawText(0, 0, w, h, 0, self.text())
        super(Label, self).paintEvent(qpaintevent)


class VersionItemWidget(QtWidgets.QWidget):

    def __init__(self, version, **kwargs):
        super(VersionItemWidget, self).__init__(**kwargs)

        self.version = version
        self.exporter = version.get_exporter()
        self.layout1 = QtWidgets.QHBoxLayout()
        self.version_label = Label()
        self.version_label.setStyleSheet('font: italic bold 17px Arial')
        self.color_label = QtWidgets.QLabel()
        self.step_label = Label()
        self.step_label.setStyleSheet('font: bold 17px Arial')
        self.layout1.addWidget(self.version_label)
        self.layout1.addStretch()
        self.layout1.addWidget(self.color_label)
        self.layout1.addWidget(self.step_label)
        self.form_layout = QtWidgets.QFormLayout()
        self.masterLayout = QtWidgets.QVBoxLayout()
        self.masterLayout.addSpacing(5)
        self.masterLayout.addLayout(self.layout1)
        self.masterLayout.addStretch()
        self.masterLayout.addLayout(self.form_layout)
        self.setLayout(self.masterLayout)
        self.masterLayout.setAlignment(QtCore.Qt.AlignTop)
        self.masterLayout.setContentsMargins(10, 0, 0, 5)
        #
        self.version_label.setText(self.version.name)
        self.color_label.setFixedSize(QtCore.QSize(20, 20))
        self.setToolTip('<font color=white>id: %s</font>' % self.version.id)
        self.entity = self.exporter.basset_url.entity
        basset_name = Label('BAsset:')
        # print self.exporter.basset_url.asset.name
        basset_label = Label(self.exporter.basset_url.asset.name)
        entity_name = Label('Entity:')
        entity_label = Label(self.entity.get_full_name())
        for label in [basset_name, entity_name, basset_label, entity_label]:
            label.setStyleSheet('font: 12px Liberation Sans')
        self.form_layout.addRow(basset_name, basset_label)
        self.form_layout.addRow(entity_name, entity_label)
        if self.entity.type == 'step':
            self.step_label.setText(self.entity.name)

        style = "background: transparent;" \
                "color: black"
        self.setStyleSheet(style)

        self.resize(200, 80)
        # self.backLabel.setFixedSize(self.width(), self.height())


class VersionItem(QtWidgets.QGraphicsItem):

    def __init__(self, version, *args, **kwargs):
        super(VersionItem, self).__init__(*args, **kwargs)

        self.x = 0
        self.y = 0
        self.w = 220
        self.h = 80

        self._parent = None
        self._children = []

        self.version = version
        self.id = version.id
        self.edges = []
        self.orientation = 0

        self.margin = 6
        self.roundness = 10
        self.base_color = QtGui.QColor(210, 210, 210)
        self.normal_color = self.base_color
        self.highlight_color = QtGui.QColor(250, 250, 150)
        self.fill_color = self.normal_color
        self.border_color = QtGui.QColor(150, 150, 210)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

        self.dependent_versions = self.version.sources
        self.dependent_versions_count = self.dependent_versions.count()

        self.destination_versions = self.version.destinations
        self.destination_versions_count = self.destination_versions.count()

        self.connected_sources = dict()
        self.connected_destinations = dict()

        self.children_populated = False
        self.parent_populated = False

        latest_version = self.version.asset.get_latest_version(status='PUB')
        if int(latest_version.id) != int(self.version.id):
            self.add_tag(WarningTag(warning='New version found!\n{0}'.format(latest_version.name)), position=0.375)

    def set_orientation(self, orientation):
        self.orientation = orientation
        if self.dependent_versions_count > 0:
            self.add_knob(OutputKnob(name="output"))
        if self.destination_versions_count > 0:
            self.add_knob(InputKnob(name="input"))

    def set_color(self, step):
        color = get_pipeline_color(step)
        self.normal_color = QtGui.QColor(color[0], color[1], color[2])
        self.fill_color = self.normal_color

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
        parent.add_child(self)

    @property
    def name(self):
        return self.version.name

    def add_child(self, child):
        self._children.append(child)
        child._parent = self

    def insert_child(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def remove_child(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def child(self, row):
        if self._children:
            return self._children[row]
        else:
            return None

    def child_count(self):
        return len(self._children)

    def boundingRect(self):
        """Return the bounding box of the Node.

        :return:
        """
        rect = QtCore.QRectF(self.x,
                             self.y,
                             self.w,
                             self.h)

        return rect

    def connect_source(self, node):
        if node.id not in self.connected_sources.keys():
            self.knob("output").connect_to(node.knob("input"), orientation=self.orientation)
            self.connected_sources[node.id] = node
            node.connected_destinations[self.id] = self

    def connect_destination(self, node):
        if node.id not in self.connected_destinations.keys():
            node.knob("output").connect_to(self.knob("input"), orientation=self.orientation)
            self.connected_destinations[node.id] = node
            node.connected_sources[self.id] = self

    def populate_children(self, populate_layer=1, reset_pos=False):
        if not self.children_populated:
            if populate_layer > 0:
                populate_layer = populate_layer - 1

                if not self.version:
                    return 0
                if not self.dependent_versions:
                    return 0

                self.scene().max_y_depth += self.dependent_versions_count
                self.scene().depth += 1

                padding_x = 200
                padding_y = 30

                # top, right, bottom, left = [self.y, 10, 10, 10 + self.x + self.w]
                if self.orientation == 0:
                    x = padding_x + self.pos().x() + self.w + 100 * self.dependent_versions_count
                    y = self.pos().y()
                else:
                    x = self.pos().x()
                    y = padding_x + self.pos().y() + self.h + 100 * self.dependent_versions_count

                all_count = self.dependent_versions_count

                for v in self.dependent_versions:
                    version_exist = False
                    for i in self.scene().items():
                        if isinstance(i, VersionItem):
                            if i.version == v:
                                dependent_item = i
                                version_exist = True
                                break
                    if not version_exist or not self.scene().combine_version:
                        if v.id not in self.connected_sources:
                            dependent_item = VersionItem.create_item(v)
                            self.scene().addItem(dependent_item)
                            dependent_item.set_orientation(self.orientation)
                            dependent_item.parent = self
                            dependent_item.setPos(x, y)
                            dependent_item.show_version_widget()
                        else:
                            dependent_item = self.connected_sources[v.id]
                    self.connect_source(dependent_item)

                    # y += padding_y + dependent_item.h

                    children_count = dependent_item.populate_children(populate_layer, reset_pos)
                    all_count += children_count
                    if self.orientation == 0:
                        y += (padding_y + dependent_item.h) * max(children_count, 1)
                    else:
                        x += (padding_y + dependent_item.w) * max(children_count, 1)

                    QtCore.QCoreApplication.processEvents()

                if reset_pos:
                    if self.orientation == 0:
                        self.setPos(self.pos().x(),
                                    self.pos().y() + (y - padding_y - self.pos().y()) / 2 -self.h / 2)
                    else:
                        self.setPos(self.pos().x() + (x - padding_y - self.pos().x()) / 2 -self.w / 2,
                                    self.pos().y())
                    self.update_edge(self)

                self.children_populated = True
                return all_count
            else:
                return 0
        return 0

    def populate_parent(self):
        if not self.parent_populated:
            padding_x = 200
            padding_y = 30

            if self.orientation == 0:
                x = self.pos().x() - padding_x - self.w - 100 * self.destination_versions_count
                y = self.pos().y()
            else:
                x = self.pos().x()
                y = self.pos().y() - padding_x - self.h - 100 * self.destination_versions_count

            for v in self.destination_versions:
                version_exist = False
                for i in self.scene().items():
                    if isinstance(i, VersionItem):
                        if i.version == v:
                            destination_item = i
                            version_exist = True
                            break
                if not version_exist:
                    # if v.id not in self.connected_destinations:
                    destination_item = VersionItem.create_item(v)
                    self.scene().addItem(destination_item)
                    destination_item.set_orientation(self.orientation)
                    self.parent = destination_item
                    destination_item.setPos(x, y)
                    destination_item.show_version_widget()
                    # else:
                    #     destination_item = self.connected_destinations[v.id]
                self.connect_destination(destination_item)

                if self.orientation == 0:
                    y += (padding_y + destination_item.h)
                else:
                    x += (padding_y + destination_item.w)

                QtCore.QCoreApplication.processEvents()
            self.parent_populated = True

    def knobs(self, cls=None):
        """Return a list of childItems that are Knob objects.

        If the optional `cls` is specified, return only Knobs of that class.
        This is useful e.g. to get all InputKnobs or OutputKnobs.
        """
        knobs = []
        for child in self.childItems():
            if isinstance(child, Knob):
                knobs.append(child)

        if cls:
            knobs = filter(knobs, lambda k: k.__class__ is cls)

        return knobs

    def knob(self, name):
        """Return matching Knob by its name, None otherwise."""
        for knob in self.knobs():
            if knob.name == name:
                return knob
        return None

    def add_knob(self, knob):
        """Add the given Knob to this Node.

        A Knob must have a unique name, meaning there can be no duplicates within
        a Node (the displayNames are not constrained though).

        Assign ourselves as the Knob's parent item (which also will put it onto
        the current scene, if not yet done) and adjust or size for it.

        The position of the Knob is set relative to this Node and depends on it
        either being an Input- or OutputKnob.
        """
        knob_names = [k.name for k in self.knobs()]
        if knob.name in knob_names:
            raise DuplicateKnobNameError(
                "Knob names must be unique, but {0} already exists."
                .format(knob.name))

        # children = [c for c in self.childItems()]

        # y_offset = sum([c.h + self.margin for c in children if isinstance(c, Knob)])
        x_offset = self.margin / 2

        knob.setParentItem(self)
        knob.margin = self.margin

        bbox = self.boundingRect()
        y_offset = (bbox.height() - knob.h) / 2
        if isinstance(knob, OutputKnob):
            if self.orientation == 0:
                knob.setPos(bbox.right() - knob.w + x_offset, y_offset)
            else:
                knob.setPos(bbox.width() / 2, bbox.bottom() - x_offset)
        elif isinstance(knob, InputKnob):
            if self.orientation == 0:
                knob.setPos(bbox.left() - x_offset, y_offset)
            else:
                knob.setPos(bbox.width() / 2, bbox.top() - x_offset)

    def tags(self, cls=None):
        """Return a list of childItems that are Knob objects.

        If the optional `cls` is specified, return only Knobs of that class.
        This is useful e.g. to get all InputKnobs or OutputKnobs.
        """
        tags = []
        for child in self.childItems():
            if isinstance(child, (Tag, PixmapTag)):
                tags.append(child)

        if cls:
            tags = filter(tags, lambda k: k.__class__ is cls)

        return tags

    def add_tag(self, tag_item, position=0.0):
        tag_item.setParentItem(self)
        margin_x = tag_item.w / 2.0 + TAG_MARGIN
        margin_y = tag_item.h / 2.0 + TAG_MARGIN
        if position <= 0.25:
            y = 0 - margin_y
            x = position * (self.w + margin_x * 2) / 0.25 - margin_x
        elif 0.25 < position <= 0.5:
            x = (self.w + margin_x * 2) - margin_x
            y = (position - 0.25) * (self.h + margin_y * 2.0) / 0.25 - margin_y
        elif 0.5 < position <= 0.75:
            x = (position - 0.5) * (-2.0 * margin_x - self.w) / 0.25 + (self.w + margin_x)
            y = self.h + margin_y
        elif 0.75 < position <= 1.0:
            x = 0 - margin_x
            y = (position - 0.75) * (-2.0 * margin_y - self.h) / 0.25 + (self.h + margin_y)
        tag_item.setPos(x - tag_item.w / 2.0, y - tag_item.h / 2.0)

    def set_highlight(self, value=True):
        if value:
            self.fill_color = self.highlight_color
        else:
            self.fill_color = self.normal_color

    def paint(self, painter, option, widget):
        bbox = self.boundingRect()
        if self.isSelected():
            self.set_highlight()
            pen = QtGui.QPen(self.border_color)
            pen.setWidth(2)
            painter.setPen(pen)

            painter.setBrush(QtGui.QBrush(self.fill_color))
            painter.drawRoundedRect(self.x,
                                    self.y,
                                    bbox.width(),
                                    self.h,
                                    self.roundness,
                                    self.roundness)
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

            painter.setBrush(QtGui.QBrush(self.base_color))
            # painter.setBrush(QtGui.QBrush(self.fill_color))
            painter.drawRoundedRect(self.x,
                                    self.y,
                                    bbox.width(),
                                    self.h,
                                    self.roundness,
                                    self.roundness)

            painter.setBrush(QtGui.QBrush(self.fill_color))
            painter.drawRect(self.x,
                             self.y + self.roundness,
                             bbox.width(),
                             self.h - 50 - self.roundness)
            painter.drawRoundedRect(self.x,
                                    self.y,
                                    bbox.width(),
                                    self.h - 50,
                                    self.roundness,
                                    self.roundness)

    def show_version_widget(self):
        self.version_widget = VersionItemWidget(self.version)
        self.set_color(self.version_widget.entity.name)
        self.version_widget_proxy = self.scene().addWidget(self.version_widget)
        self.version_widget_proxy.setParentItem(self)
        self.version_widget_proxy.setPos(0, 0)
        # print self.version_widget_proxy.pos()
        # print self.version_widget_proxy.size()
        # QtWidgets.QGraphicsProxyWidget.setPos()

        self.create_context_menu()

    def add_edge(self, edge):
        self.edges.append(edge)
        scene = self.scene()
        if edge not in scene.items():
            scene.addItem(edge)

    def update_edge(self, item):
        for knob in item.knobs():
            for edge in knob.edges:
                edge.update_path(self.orientation)

    def mouseMoveEvent(self, event):
        for item in self.scene().selectedItems():
            self.update_edge(item)
        super(VersionItem, self).mouseMoveEvent(event)

    def create_context_menu(self):
        self.menu = QtWidgets.QMenu(self.scene().parent())
        self.show_detail_action = QtWidgets.QAction("Open in Browser", self.menu)
        self.show_detail_action.triggered.connect(self._show_details_action_triggered)
        self.open_in_file_action = QtWidgets.QAction("Open in File Browser", self.menu)
        self.open_in_file_action.triggered.connect(self._open_file_action_triggered)
        self.menu.addAction(self.show_detail_action)
        self.menu.addAction(self.open_in_file_action)

        self.menu.setStyleSheet("""
        QMenu::item:selected{
            background:rgb(100, 100, 150)
        }
        """)

    def contextMenuEvent(self, event):
        super(VersionItem, self).contextMenuEvent(event)
        self.menu.move(QtGui.QCursor().pos())
        self.menu.show()

    def _show_details_action_triggered(self):
        open_version_in_browser(self.version)

    def _open_file_action_triggered(self):
        open_version_in_file_explorer(self.version)

    def log(self, tab_level=-1):

        output = ""
        tab_level += 1

        for i in range(tab_level):
            output += "\t"

        output += "|--" + self.name + "\n"

        for child in self._children:
            output += child.log(tab_level)

        tab_level -= 1
        output += "\n"

        return output

    def __repr__(self):
        return self.log()

    def mouseDoubleClickEvent(self, event):
        super(VersionItem, self).mouseDoubleClickEvent(event)
        self.scene().parent().itemDoubleClicked.emit(self.version)

    @classmethod
    def create_item(cls, version, *args, **kwargs):
        if version.get_exporter().basset_url.entity.name == 'cmp':
            item = CmpVersionItem(version, *args, **kwargs)
        elif version.get_exporter().basset_url.entity.name == 'pla':
            item = PlaVersionItem(version, *args, **kwargs)
        else:
            item = VersionItem(version, *args, **kwargs)
        return item


class CmpVersionItem(VersionItem):
    def __init__(self, version, *args, **kwargs):
        super(CmpVersionItem, self).__init__(version, *args, **kwargs)


class PlaVersionItem(VersionItem):
    def __init__(self, version, *args, **kwargs):
        super(PlaVersionItem, self).__init__(version, *args, **kwargs)

        self.basset_name = self.version.get_exporter().basset_url.asset.name

    def set_color(self, step):
        if self.basset_name == 'cc_bundle':
            self.normal_color = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(self.w, 0))
            self.normal_color.setColorAt(0, QtGui.QColor(200, 20, 20))
            self.normal_color.setColorAt(1, QtGui.QColor(55, 55, 255))
            self.fill_color = self.normal_color
        else:
            super(PlaVersionItem, self).set_color(step)

