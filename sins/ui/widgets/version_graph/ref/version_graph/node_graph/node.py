# -*- coding: utf-8 -*-

from BQt import QtGui, QtCore, QtWidgets
from knob import InputKnob, OutputKnob, Knob
from tag import Tag, PixmapTag, WarningTag
from item_widget import VersionItemWidget
from errors import DuplicateKnobNameError
from bfx.ui.version_graph.utils import open_version_in_browser, open_version_in_file_explorer
from bfx.ui.util import get_pipeline_color
from bfx.util.log import log_time_cost
from bfx.data.ple.assets import Entity, Asset
import time

TAG_MARGIN = 3
PADDING_X = 200
PADDING_Y = 30
SPECIAL_COLOR = {
    'cc_bundle': [[200, 80, 80], [115, 115, 255]]
}


class VersionItem(QtWidgets.QGraphicsItem):

    def __init__(self, version, entity, asset, *args, **kwargs):
        super(VersionItem, self).__init__(*args, **kwargs)

        self.x = 0
        self.y = 0
        self.w = 220
        self.h = 80

        self._parent = None
        self._children = []

        self.version = version
        self.entity = entity
        self.asset = asset
        self.id = version.id
        self.edges = []
        self.orientation = 0

        self.margin = 6
        self.roundness = 10
        self.base_color = QtGui.QColor(210, 210, 210)
        self.base_color = QtGui.QColor(50, 60, 70)
        self.normal_color = self.base_color
        self.highlight_color = QtGui.QColor(250, 250, 150)
        self.highlight_color = QtGui.QColor(230, 230, 100)
        self.fill_color = self.normal_color
        self.border_color = QtGui.QColor(150, 150, 210)
        self.border_color = QtGui.QColor(180, 180, 250)

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

    def check_new_version(self):
        latest_version = self.asset.get_latest_version(status='PUB')
        if int(latest_version.id) != int(self.version.id):
            self.add_tag(WarningTag(warning='New version found!\n{0}'.format(latest_version.name)), position=0.875)

    def set_orientation(self, orientation):
        self.orientation = orientation
        if self.dependent_versions_count > 0:
            self.add_knob(OutputKnob(name="output"))
        if self.destination_versions_count > 0:
            self.add_knob(InputKnob(name="input"))

    def set_color(self, step):
        color = get_pipeline_color(step)
        self.normal_color = QtGui.QColor(color[0], color[1], color[2], 200)
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

    @log_time_cost
    def populate_children(self, populate_layer=1, reset_pos=False):
        if not self.children_populated:
            if populate_layer > 0:
                self.populate_layer = populate_layer - 1
                self.reset_pos = reset_pos

                if not self.version:
                    return 0, 0
                if not self.dependent_versions:
                    return 0, 0

                self.scene().max_y_depth += self.dependent_versions_count
                self.scene().depth += 1

                # top, right, bottom, left = [self.y, 10, 10, 10 + self.x + self.w]
                if self.orientation in [0, 2]:
                    if self.orientation == 0:
                        self.temp_x = self.pos().x() + PADDING_X + self.w + 50 * self.dependent_versions_count
                    else:
                        self.temp_x = self.pos().x() - PADDING_X - 50 * self.dependent_versions_count
                    self.temp_y = self.pos().y()
                elif self.orientation in [1, 3]:
                    self.temp_x = self.pos().x()
                    if self.orientation == 1:
                        self.temp_y = self.pos().y() + PADDING_X + self.h + 50 * self.dependent_versions_count
                    else:
                        self.temp_y = self.pos().y() - PADDING_X - 50 * self.dependent_versions_count

                self.all_count = self.dependent_versions_count
                # self.max_y = self.pos().y()

                for index, v in enumerate(self.dependent_versions):
                    # version_exist = False
                    # for i in self.scene().items():
                    #     if isinstance(i, VersionItem):
                    #         if i.version == v:
                    #             dependent_item = i
                    #             version_exist = True
                    #             break
                    # if not version_exist or not self.scene().combine_version:
                    #     if v.id not in self.connected_sources:
                    #         t = time.time()
                    #         dependent_item = VersionItem.create_item(v)
                    #         self.scene().addItem(dependent_item)
                    #         dependent_item.set_orientation(self.orientation)
                    #         dependent_item.parent = self
                    #         dependent_item.setPos(x, y)
                    #         dependent_item.show_version_widget()
                    #         print time.time() - t, v.id
                    #     else:
                    #         dependent_item = self.connected_sources[v.id]
                    # self.connect_source(dependent_item)
                    #
                    # # self.temp_y += PADDING_Y + dependent_item.h
                    #
                    # children_count = dependent_item.populate_children(populate_layer, reset_pos)
                    # self.all_count += children_count
                    # if self.orientation == 0:
                    #     self.temp_y += (PADDING_Y + dependent_item.h) * max(children_count, 1)
                    # else:
                    #     self.temp_x += (PADDING_Y + dependent_item.w) * max(children_count, 1)
                    #
                    # QtCore.QCoreApplication.processEvents()
                    self.populate_child(index)

                # QtCore.QCoreApplication.postEvent(self.scene().parent(), PopulateEvent(0, self))
                # self.scene().parent().itemPopulate.emit(0, self)

                if self.reset_pos:
                    if self.orientation in [0, 2]:
                        self.setPos(self.pos().x(),
                                    self.pos().y() + (self.temp_y - PADDING_Y - self.pos().y()) / 2 -self.h / 2)
                    elif self.orientation in [1, 3]:
                        self.setPos(self.pos().x() + (self.temp_x - PADDING_Y - self.pos().x()) / 2 -self.w / 2,
                                    self.pos().y())
                    self.update_edge(self)

                self.children_populated = True
                return self.all_count, 0
            else:
                return 0, 0
        return 0, 0

    def populate_child(self, index):
        t0 = time.time()
        v = self.dependent_versions[index]
        version_exist = False
        t1 = time.time()
        for i in self.scene().items():
            if isinstance(i, VersionItem):
                if i.version == v:
                    dependent_item = i
                    version_exist = True
                    break
        # print time.time() - t1
        if not version_exist or not self.scene().combine_version:
            if v.id not in self.connected_sources:
                t1 = time.time()
                dependent_item = VersionItem.create_item(v)
                self.scene().addItem(dependent_item)
                dependent_item.set_orientation(self.orientation)
                dependent_item.parent = self
                dependent_item.setPos(self.temp_x, self.temp_y)
                dependent_item.set_color(dependent_item.entity.name)
                # dependent_item.show_version_widget()
                # print time.time() - t1, v.id
            else:
                dependent_item = self.connected_sources[v.id]
        self.connect_source(dependent_item)

        # self.temp_y += PADDING_Y + dependent_item.h

        children_count, max_y = dependent_item.populate_children(self.populate_layer, self.reset_pos)
        self.all_count += children_count
        # self.max_y = max(self.max_y, max_y)
        # if not version_exist:
        if self.orientation in [0, 2]:
            self.temp_y += (PADDING_Y + dependent_item.h) * max(children_count, 1)
            # self.temp_y += (PADDING_Y + dependent_item.h) + self.max_y
        elif self.orientation in [1, 3]:
            self.temp_x += (PADDING_Y + dependent_item.w) * max(children_count, 1)

        # print time.time() - t0

        QtCore.QCoreApplication.processEvents()

    def populate_parent(self):
        if not self.parent_populated:
            PADDING_X = 200
            PADDING_Y = 30

            if self.orientation in [0, 2]:
                if self.orientation == 0:
                    x = self.pos().x() - PADDING_X - self.w - 50 * self.destination_versions_count
                else:
                    x = self.pos().x() + PADDING_X + self.w + 50 * self.destination_versions_count
                y = self.pos().y()
            elif self.orientation in [1, 3]:
                x = self.pos().x()
                if self.orientation == 1:
                    y = self.pos().y() - PADDING_X - self.h - 50 * self.destination_versions_count
                else:
                    y = self.pos().y() + PADDING_X + self.h + 50 * self.destination_versions_count

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
                    destination_item.set_color(destination_item.entity.name)
                    # destination_item.show_version_widget()
                    # else:
                    #     destination_item = self.connected_destinations[v.id]
                self.connect_destination(destination_item)

                if self.orientation in [0, 2]:
                    y += (PADDING_Y + destination_item.h)
                elif self.orientation in [1, 3]:
                    x += (PADDING_Y + destination_item.w)

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
                knob.setPos(bbox.right() - knob.w / 2.0, y_offset)
            elif self.orientation == 1:
                knob.setPos(bbox.width() / 2, bbox.bottom() - knob.w / 2.0)
            elif self.orientation == 2:
                knob.setPos(bbox.left() - knob.w / 2.0, y_offset)
            elif self.orientation == 3:
                knob.setPos(bbox.width() / 2, bbox.top() - knob.w / 2.0)
        elif isinstance(knob, InputKnob):
            if self.orientation == 0:
                knob.setPos(bbox.left() - knob.w / 2.0, y_offset)
            elif self.orientation == 1:
                knob.setPos(bbox.width() / 2, bbox.top() - knob.w / 2.0)
            elif self.orientation == 2:
                knob.setPos(bbox.right() - knob.w + knob.w / 2.0, y_offset)
            elif self.orientation == 3:
                knob.setPos(bbox.width() / 2, bbox.bottom() - knob.w / 2.0)

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
        if hasattr(self, 'version_widget'):
            self.version_widget.set_highlight(value)

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
            # painter.drawRoundedRect(self.x,
            #                         self.y,
            #                         bbox.width(),
            #                         self.h,
            #                         self.roundness,
            #                         self.roundness)
            #
            # painter.setBrush(QtGui.QBrush(self.fill_color))
            # painter.drawRect(self.x,
            #                  self.y + self.roundness,
            #                  bbox.width(),
            #                  self.h - 50 - self.roundness)
            # painter.drawRoundedRect(self.x,
            #                         self.y,
            #                         bbox.width(),
            #                         self.h - 50,
            #                         self.roundness,
            #                         self.roundness)

            painter.setBrush(QtGui.QBrush(self.fill_color))
            painter.drawRoundedRect(self.x,
                                    self.y,
                                    bbox.width(),
                                    self.h,
                                    self.roundness,
                                    self.roundness)
            painter.setBrush(QtGui.QBrush(self.base_color))
            painter.drawRect(self.x,
                             self.y + 30,
                             bbox.width(),
                             self.h - 30 - self.roundness)
            painter.drawRoundedRect(self.x,
                                    self.y + 30,
                                    bbox.width(),
                                    self.h - 30,
                                    self.roundness,
                                    self.roundness)


    def start_show_version_widget(self):
        # self.scene().parent().showWidgetSignal.emit(self)
        QtCore.QCoreApplication.postEvent(self.scene().parent(), ShowVersionWidgetEvent(self))

    def show_version_widget(self):
        # print 'show_version_widget'
        if not hasattr(self, 'version_widget'):
            self.version_widget = VersionItemWidget.create_item(self.version, self.entity, self.asset)
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
        self.scene().parent().itemDoubleClicked.emit(self)

    # def sceneEvent(self, event):
    #     return super(VersionItem, self).sceneEvent(event)

    @classmethod
    def create_item(cls, version, *args, **kwargs):
        t = time.time()
        # exporter = version.get_exporter()
        # basset_url = exporter.basset_url
        # entity = basset_url.entity
        # asset = basset_url.asset

        # basset_url._get_common_basset_parse_result()
        # entity = basset_url.result["_common_basset_parse_result"]['entity']
        # asset = basset_url.result["_common_basset_parse_result"]['asset']

        # entity = Entity.find(basset_url.path)

        asset = version.asset
        entities = asset.entities
        try:
            entity = entities[0]
        except:
            exporter = version.get_exporter()
            basset_url = exporter.basset_url
            entity = Entity.find(basset_url.path)

        # print 'exporter:', time.time() - t
        if entity.name == 'cmp':
            item = CmpVersionItem(version, entity, asset, *args, **kwargs)
        elif entity.name == 'pla':
            item = PlaVersionItem(version, entity, asset, *args, **kwargs)
        else:
            item = VersionItem(version, entity, asset, *args, **kwargs)
        # item = VersionItem(version, *args, **kwargs)
        return item


class CmpVersionItem(VersionItem):
    def __init__(self, version, entity, asset, *args, **kwargs):
        super(CmpVersionItem, self).__init__(version, entity, asset, *args, **kwargs)


class PlaVersionItem(VersionItem):
    def __init__(self, version, entity, asset, *args, **kwargs):
        super(PlaVersionItem, self).__init__(version, entity, asset, *args, **kwargs)

        self.basset_name = asset.name

    def set_color(self, step):
        if self.basset_name == 'cc_bundle':
            self.normal_color = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(self.w, 0))
            color1 = SPECIAL_COLOR['cc_bundle'][0]
            color2 = SPECIAL_COLOR['cc_bundle'][1]
            self.normal_color.setColorAt(0, QtGui.QColor(color1[0], color1[1], color1[2]))
            self.normal_color.setColorAt(1, QtGui.QColor(color2[0], color2[1], color2[2]))
            self.fill_color = self.normal_color
        else:
            super(PlaVersionItem, self).set_color(step)


class PopulateEvent(QtCore.QEvent):
    eventType = QtCore.QEvent.registerEventType()

    def __init__(self, index, item):
        super(PopulateEvent, self).__init__(PopulateEvent.eventType)

        self.index = index
        self.item = item


class ShowVersionWidgetEvent(QtCore.QEvent):
    eventType = QtCore.QEvent.registerEventType()

    def __init__(self, item):
        super(ShowVersionWidgetEvent, self).__init__(ShowVersionWidgetEvent.eventType)

        self.item = item

