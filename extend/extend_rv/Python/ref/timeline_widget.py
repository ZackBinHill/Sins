# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 5/3/2018

# import os
import sys
# from PySide.QtGui import *
# from PySide.QtCore import *
from BQt import QtWidgets, QtGui, QtCore
import math

in_rv = False
try:
    import rv
    in_rv = True
except ImportError:
    pass


TIME_SLIDER_HEIGHT = 20
TRACK_HEIGHT = 45
LABEL_MARGIN = 5
HEADER_WIDTH = 150
TRACK_GAP = 3


# rv functions
def get_node_range(node):
    if in_rv:
        noderange = rv.commands.nodeRangeInfo(node)
        noderange['duration'] = noderange['cutOut'] - noderange['cutIn'] + 1
        return noderange
    else:
        noderange = {'start': 0, 'end': 10, 'cutIn': 1, 'cutOut': 5, 'fps': 24.0}
        noderange['duration'] = noderange['cutOut'] - noderange['cutIn'] + 1
        return noderange


def get_ui_name(node):
    if in_rv:
        return rv.extra_commands.uiName(node)
    else:
        return 'None'


def get_type_of_node(node):
    if in_rv:
        return rv.commands.nodeType(node)
    else:
        return ''


def get_inputs(node):
    if in_rv:
        nodeType = get_type_of_node(node)
        if nodeType in ['RVStackGroup', 'RVSwitchGroup', 'RVSequenceGroup']:
            return rv.commands.nodeConnections(node)[0]
        else:
            return [node]
    else:
        return []


def source_of_group(groupNode):
    for node in rv.commands.nodesInGroup(groupNode):
        if get_type_of_node(node) == 'RVFileSource':
            return node


def is_gap(node):
    if in_rv:
        source = source_of_group(node)
        mediaSource = rv.commands.sourceMedia(source)[0]
        if mediaSource.split('.')[-1] == 'movieproc':
            return True
        else:
            return False
    else:
        return False


def is_source_group(node):
    if in_rv:
        if get_type_of_node(node) == 'RVSourceGroup':
            return True
        else:
            return False
    else:
        return False


def view_node(node):
    if in_rv:
        rv.commands.setViewNode(node)
    else:
        pass


def create_new_node(selected_nodes, to_node_type):
    # print selected_nodes
    n = len(selected_nodes)
    node = rv.commands.newNode(to_node_type)
    basename = to_node_type[0:-5]
    if n == 0:
        name = 'Empty {}'.format(basename)
    elif n < 3:
        name = '{} of '.format(basename)
        for i, input in enumerate(selected_nodes):
            if (i > 0 and n > 2):
                name += ','
            if i > 0:
                name += ' '
            if (i == n - 1 and n > 1):
                name += 'and '
            name += rv.extra_commands.uiName(input)
    else:
        name = '{} of {} views'.format(basename, n)
    rv.extra_commands.setUIName(node, name)
    rv.commands.setNodeInputs(node, selected_nodes)
    view_node(node)


def get_cut_in(node):
    return get_node_range(node)['cutIn']


def get_cut_out(node):
    return get_node_range(node)['cutOut']


def get_fps(node):
    return get_node_range(node)['fps']


def get_cut_start(node):
    return get_node_range(node)['start']


def get_cut_end(node):
    return get_node_range(node)['end']


def get_cut_duration(node):
    return get_node_range(node)['duration']


def get_current_view():
    if in_rv:
        return rv.commands.viewNode()
    else:
        return None


def set_cut_in_out(in_point=None, out_point=None):
    if in_rv:
        if in_point is not None:
            rv.commands.setInPoint(in_point)
        if out_point is not None:
            rv.commands.setOutPoint(out_point)


def set_frame(frame):
    if in_rv:
        rv.commands.setFrame(frame)


def get_frame():
    if in_rv:
        return rv.commands.frame()


def get_timeline_range(index, sequence):
    if in_rv:
        if get_type_of_node(sequence) != 'RVSourceGroup':
            current_inputs = get_inputs(sequence)
            if index < len(current_inputs):
                start_frame = 0
                for j, node in enumerate(current_inputs):
                    # print node
                    if j != index:
                        start_frame += get_cut_duration(node)
                    else:
                        source = node
                        break
                # print start_frame
                return start_frame, start_frame + get_cut_duration(source) - 1
        else:
            start_frame = get_cut_in(sequence) - 1
            # print 'start:', start_frame
            return start_frame, start_frame + get_cut_duration(sequence) - 1

    else:
        return 0, 10


def get_tracks_from_view(node):
    if in_rv:
        nodeType = get_type_of_node(node)
        if nodeType in ['RVStackGroup', 'RVSwitchGroup']:
            return get_inputs(node)
        elif nodeType == 'RVSequenceGroup':
            return [node]
        elif nodeType == 'RVSourceGroup':
            return [node]
        else:
            return []
    else:
        return []


def get_rect_from_view(node):
    if in_rv:
        width = get_cut_duration(node)
        height = 0
        nodeType = get_type_of_node(node)
        if nodeType in ['RVStackGroup', 'RVSwitchGroup']:
            height = TIME_SLIDER_HEIGHT + len(get_inputs(node)) * TRACK_HEIGHT
        elif nodeType == 'RVSequenceGroup':
            height = TIME_SLIDER_HEIGHT + 1 * TRACK_HEIGHT
        elif nodeType == 'RVSourceGroup':
            width = get_cut_duration(node) + get_cut_in(node)
            height = TIME_SLIDER_HEIGHT + 1 * TRACK_HEIGHT
        return 0, 0, width, height
    else:
        return 0, 0, 1000, 100


def is_timeline(node):
    if in_rv:
        nodeType = get_type_of_node(node)
        if nodeType in ['RVStackGroup', 'RVSwitchGroup', 'RVSequenceGroup', 'RVSourceGroup']:
            return True
        else:
            return False
    else:
        return True


def to_timecode(frame, rate=None):

    if frame is None:
        return None

    # First, we correct the time unit total as if the content were playing
    # back at "nominal" fps
    nominal_fps = math.ceil(rate)
    time_units_per_second = rate
    time_units_per_frame = time_units_per_second / nominal_fps
    time_units_per_minute = time_units_per_second * 60
    time_units_per_hour = time_units_per_minute * 60
    time_units_per_day = time_units_per_hour * 24

    days, hour_units = divmod(frame, time_units_per_day)
    hours, minute_units = divmod(hour_units, time_units_per_hour)
    minutes, second_units = divmod(minute_units, time_units_per_minute)
    seconds, frame_units = divmod(second_units, time_units_per_second)
    frames, _ = divmod(frame_units, time_units_per_frame)

    channels = (hours, minutes, seconds, frames)

    return ":".join(
        ["{n:0{width}d}".format(n=int(n), width=2) for n in channels]
    )


class _BaseItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, nodename=None, index=0, *args, **kwargs):
        super(_BaseItem, self).__init__(*args, **kwargs)
        self.nodename = nodename
        self.index = index
        self.moveItem = False

        self.linearGrad = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(0, TRACK_HEIGHT))
        self.linearGrad.setColorAt(0, QtGui.QColor(75, 75, 75))
        self.linearGrad.setColorAt(1, QtGui.QColor(55, 55, 55))

        # self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        # self.setBrush(QtGui.QBrush(QtGui.QColor(180, 180, 180, 255)))
        self.setBrush(QtGui.QBrush(self.linearGrad))

        self.cut_in_label = QtWidgets.QGraphicsSimpleTextItem(self)
        self.cut_out_label = QtWidgets.QGraphicsSimpleTextItem(self)
        self.source_name_label = QtWidgets.QGraphicsSimpleTextItem(self)

        self._set_labels()
        self.update_size()

        self.textColor = QtGui.QColor(220, 220, 220)
        self.cut_in_label.setBrush(QtGui.QBrush(self.textColor))
        self.cut_out_label.setBrush(QtGui.QBrush(self.textColor))
        self.source_name_label.setBrush(QtGui.QBrush(self.textColor))

    def paint(self, *args, **kwargs):
        new_args = [args[0], QtWidgets.QStyleOptionGraphicsItem()] + list(args[2:])
        super(_BaseItem, self).paint(*new_args, **kwargs)

    def update_size(self):
        noderange = get_node_range(self.nodename)
        duration = noderange['duration']
        rect = QtCore.QRectF(
            0,
            0,
            duration,
            TRACK_HEIGHT
        )
        self.setRect(rect)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            self.setPen(
                QtGui.QColor(0, 255, 0, 255) if self.isSelected()
                else QtGui.QColor(0, 0, 0, 255)
            )
            self.setZValue(
                self.zValue() + 1 if self.isSelected() else self.zValue() - 1
            )

        return super(_BaseItem, self).itemChange(change, value)

    def _position_labels(self):
        self.cut_in_label.setY(LABEL_MARGIN)
        self.cut_out_label.setY(LABEL_MARGIN)
        self.source_name_label.setY(
            TRACK_HEIGHT
            - LABEL_MARGIN
            - self.source_name_label.boundingRect().height()
        )

    def _set_labels_rational_time(self):
        noderange = get_node_range(self.nodename)
        self.cut_in_label.setText(
            '{value}\n@{rate}'.format(
                value=noderange['cutIn'],
                rate=noderange['fps']
            )
        )
        self.cut_out_label.setText(
            '{value}\n@{rate}'.format(
                value=noderange['cutOut'],
                rate=noderange['fps']
            )
        )

    def _set_labels_timecode(self):
        noderange = get_node_range(self.nodename)
        cut_in = noderange['cut_in']
        cut_out = noderange['cut_out']
        fps = noderange['fps']
        trimmed_in, trimmed_out = get_timeline_range(self.index, self.parentItem().sequence)
        self.cut_in_label.setText('{timeline}\n{source}'.format(
                timeline=to_timecode(trimmed_in, fps),
                source=to_timecode(cut_in, fps)
            )
        )

        self.cut_out_label.setText('{timeline}\n{source}'.format(
                timeline=to_timecode(trimmed_out, fps),
                source=to_timecode(cut_out, fps)
            )
        )

    def _set_labels(self):
        self._set_labels_rational_time()
        # self._set_labels_timecode()
        self.source_name_label.setText('PLACEHOLDER')
        self._position_labels()

    def update_geo(self):
        self._set_labels_rational_time()
        self.update_size()

    def counteract_zoom(self, zoom_level=1.0):
        for label in (
            self.source_name_label,
            self.cut_in_label,
            self.cut_out_label
        ):
            label.setTransform(QtGui.QTransform.fromScale(zoom_level, 1.0))

        self_rect = self.boundingRect()
        name_width = self.source_name_label.boundingRect().width() * zoom_level
        in_width = self.cut_in_label.boundingRect().width() * zoom_level
        out_width = self.cut_out_label.boundingRect().width() * zoom_level

        frames_space = in_width + out_width + 3 * LABEL_MARGIN * zoom_level

        if frames_space > self_rect.width():
            self.cut_in_label.setVisible(False)
            self.cut_out_label.setVisible(False)
        else:
            self.cut_in_label.setVisible(True)
            self.cut_out_label.setVisible(True)

            self.cut_in_label.setX(LABEL_MARGIN * zoom_level)

            self.cut_out_label.setX(
                self_rect.width() - LABEL_MARGIN * zoom_level - out_width
            )

        total_width = (name_width + frames_space + LABEL_MARGIN * zoom_level)
        if total_width > self_rect.width():
            self.source_name_label.setVisible(False)
        else:
            self.source_name_label.setVisible(True)
            self.source_name_label.setX(0.5 * (self_rect.width() - name_width))

    def mousePressEvent(self, event):
        # if event.button() == QtCore.Qt.LeftButton:
        #     self.moveItem = True
        #     self.prevPos = event.pos()
        # else:
        #     self.moveItem = False

        super(_BaseItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.moveItem:
            mouse_move = event.pos() - self.prevPos
            move_steps = int(mouse_move.x())
            affect_tracks = []
            for item in self.scene().selectedItems():
                if item.parentItem() not in affect_tracks:
                    affect_tracks.append(item.parentItem())

            for track in affect_tracks:
                track.move_selected_by(move_steps)

    def mouseReleaseEvent(self, event):
        self.moveItem = False
        super(_BaseItem, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        view_node(self.nodename)

    def create_context_menu(self):
        self.menu = QtWidgets.QMenu(self.scene().parent())
        self.new_seq_action = QtWidgets.QAction("Create New Sequence", self.menu)
        self.new_stack_action = QtWidgets.QAction("Create New Stack", self.menu)
        self.new_switch_action = QtWidgets.QAction("Create New Switch", self.menu)
        self.mark_io_action = QtWidgets.QAction("Cut In Out From Selected", self.menu)
        self.mark_io_action.setShortcut(QtGui.QKeySequence('D'))
        self.menu.addAction(self.new_seq_action)
        self.menu.addAction(self.new_stack_action)
        self.menu.addAction(self.new_switch_action)
        self.menu.addAction(self.mark_io_action)

        self.new_seq_action.triggered.connect(lambda :self.create_new('RVSequenceGroup'))
        self.new_stack_action.triggered.connect(lambda :self.create_new('RVStackGroup'))
        self.new_switch_action.triggered.connect(lambda :self.create_new('RVSwitchGroup'))
        self.mark_io_action.triggered.connect(self.mark_io_from_selected)

    def contextMenuEvent(self, event):
        super(_BaseItem, self).contextMenuEvent(event)
        if len(self.scene().selectedItems()) > 1 and self in self.scene().selectedItems():
            self.menu.move(QtGui.QCursor().pos())
            self.menu.show()
            self.scene().parent().settingFrame = False

    def create_new(self, node_type):
        create_new_node([item.nodename for item in self.scene().selectedItems()], node_type)

    def mark_io_from_selected(self):
        self.scene().mark_io_from_selected()


class HeaderCellWidget(QtWidgets.QWidget):
    def __init__(self, sequence, **kwargs):
        super(HeaderCellWidget, self).__init__(**kwargs)

        self.sequence = sequence

        self.setFixedSize(HEADER_WIDTH, TRACK_HEIGHT)
        self.masterLayout = QtWidgets.QHBoxLayout()
        self.disableButton = QtWidgets.QPushButton('d')
        self.nameLabel = QtWidgets.QLabel(get_ui_name(self.sequence))
        # self.nameLabel.setFont(QFont('Arial', 5))
        # self.masterLayout.addWidget(self.disableButton)
        self.masterLayout.addStretch()
        self.masterLayout.addWidget(self.nameLabel)
        self.masterLayout.addStretch()
        self.masterLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.masterLayout)

        self.setStyleSheet("""
        background: transparent;
        color: white;
        font-size:15px
        """)


class HeaderItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, sequence, *args, **kwargs):
        super(HeaderItem, self).__init__(*args, **kwargs)
        self.sequence = sequence

        self.border_color = QtGui.QColor(0, 0, 0, 255)
        self.linearGrad = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(0, TRACK_HEIGHT))
        self.linearGrad.setColorAt(0, QtGui.QColor(75, 75, 75))
        self.linearGrad.setColorAt(1, QtGui.QColor(55, 55, 55))
        # self.setPen(QtCore.Qt.NoPen)

    def show_widget(self):
        self.headerCellWidget = HeaderCellWidget(self.sequence)
        self.headerCellWidgetProxy = self.scene().addWidget(self.headerCellWidget)
        self.headerCellWidgetProxy.setParentItem(self)

    def paint(self, painter, option, widget):
        # bbox = self.boundingRect()
        pen = QtGui.QPen(self.border_color)
        pen.setWidth(1)
        painter.setPen(pen)

        painter.setBrush(QtGui.QBrush(self.linearGrad))
        painter.drawRect(0, 0, HEADER_WIDTH, TRACK_HEIGHT)

    def mouseDoubleClickEvent(self, event):
        view_node(self.sequence)


class GapItem(_BaseItem):
    def __init__(self, *args, **kwargs):
        super(GapItem, self).__init__(*args, **kwargs)
        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setBrush(QtGui.QBrush(QtGui.QColor(50, 50, 50, 255)))
        self.source_name_label.setText('GAP')

    def mouseMoveEvent(self, event):
        pass


class ClipItem(_BaseItem):
    def __init__(self, *args, **kwargs):
        super(ClipItem, self).__init__(*args, **kwargs)
        # self.setBrush(QtGui.QBrush(QtGui.QColor(67, 67, 67, 255)))
        self.source_name_label.setText(get_ui_name(self.nodename))


class NestItem(_BaseItem):
    def __init__(self, *args, **kwargs):
        super(NestItem, self).__init__(*args, **kwargs)

        self.source_name_label.setText(get_ui_name(self.nodename))

        self.linearGrad.setColorAt(0, QtGui.QColor(75, 75, 145))
        self.linearGrad.setColorAt(1, QtGui.QColor(55, 55, 105))
        self.setBrush(QtGui.QBrush(self.linearGrad))


class TrackItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, sequence, *args, **kwargs):
        super(TrackItem, self).__init__(*args, **kwargs)
        self.sequence = sequence
        self.setPen(QtCore.Qt.NoPen)
        self.setBrush(QtGui.QBrush(QtGui.QColor(32, 32, 32, 255)))
        # self.populate()

    def populate(self):
        # print self.sequence, get_inputs(self.sequence)
        self.view = self.scene().parent()
        for index, node in enumerate(get_inputs(self.sequence)):
            if not is_source_group(node):
                new_item = NestItem(node, index)
            else:
                if not is_gap(node):
                    new_item = ClipItem(node, index)
                else:
                    new_item = GapItem(node, index)

            new_item.setParentItem(self)
            new_item.create_context_menu()
            # print new_item
            new_item.setX(float(get_timeline_range(index, self.sequence)[0]))
            if get_type_of_node(self.sequence) == 'RVSourceGroup' \
                    and get_type_of_node(self.scene().composition) in ['RVStackGroup', 'RVSwitchGroup']:
                new_item.setX(0)
            new_item.counteract_zoom(1.0 / self.view.current_zoom)
            # QCoreApplication.processEvents()

    def move_selected_by(self, x_step):
        pass


class TimeSlider(QtWidgets.QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super(TimeSlider, self).__init__(*args, **kwargs)
        self.setBrush(QtGui.QBrush(QtGui.QColor(58, 58, 58, 255)))


class CompositionScene(QtWidgets.QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(CompositionScene, self).__init__(*args, **kwargs)
        self.composition = None
        self.trackItems = []

        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(58, 58, 58, 255)))

    def set_timeline(self, node):
        for i in self.trackItems:
            self.removeItem(i)
        # self.clear()
        self.composition = node
        self._adjust_scene_size()
        self._add_time_slider()
        self._add_tracks()

    def _adjust_scene_size(self):

        x, y, w, h = get_rect_from_view(self.composition)

        self.setSceneRect(x, y, w * 2, h)

    def _add_time_slider(self):
        scene_rect = self.sceneRect()

        scene_rect.setWidth(scene_rect.width() * 10)
        scene_rect.setHeight(TIME_SLIDER_HEIGHT)
        self.addItem(TimeSlider(scene_rect))

    def _add_track(self, track, y_pos, index=None):
        scene_rect = self.sceneRect()
        rect = QtCore.QRectF(0, 0, scene_rect.width() * 10, TRACK_HEIGHT)
        new_track = TrackItem(track, rect)
        self.addItem(new_track)
        if index is not None:
            self.trackItems.insert(index, new_track)
        else:
            self.trackItems.append(new_track)
        new_track.populate()
        new_track.setPos(scene_rect.x(), y_pos)

    def rebuild_track(self, track):
        if track in get_tracks_from_view(self.composition):
            for trackItem in self.trackItems:
                if trackItem.sequence == track:
                    index = self.trackItems.index(trackItem)
                    # print 'rebulid track:', trackItem, index
                    self.trackItems.remove(trackItem)
                    self.removeItem(trackItem)
                    self._add_track(track, TIME_SLIDER_HEIGHT + index * (TRACK_HEIGHT + TRACK_GAP), index=index)

    def _add_tracks(self):
        video_tracks_top = TIME_SLIDER_HEIGHT

        tracks = get_tracks_from_view(self.composition)

        self.trackItems = []
        for i, track in enumerate(tracks):
            # print 'add track:', track
            self._add_track(track, video_tracks_top + i * (TRACK_HEIGHT + TRACK_GAP))

    def mark_io_from_selected(self):
        item0 = self.selectedItems()[0]
        cut_in, cut_out = get_timeline_range(item0.index, item0.parentItem().sequence)
        for item in self.selectedItems():
            trimmed_in, trimmed_out = get_timeline_range(item.index, item.parentItem().sequence)
            cut_in = min(cut_in, trimmed_in)
            cut_out = max(cut_out, trimmed_out)
        # print cut_in, cut_out
        set_cut_in_out(cut_in + 1, cut_out + 1)
        if get_frame() <= cut_in or get_frame() > cut_out + 1:
            set_frame(cut_in + 1)


class CompositionView(QtWidgets.QGraphicsView):
    # setFrame = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(CompositionView, self).__init__(*args, **kwargs)

        self.panning = False
        self.settingFrame = False
        self.current_zoom = 1.0
        self.current_frame = 1
        self.playing = False

        self.headerWidget = None
        self.lineColor = QtGui.QColor(255, 255, 255, 10)
        self.currentFrameLineColor = QtGui.QColor(255, 255, 100, 100)
        self.currentFrameRectColor = QtGui.QColor(255, 255, 100, 20)

        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.compositionScene = CompositionScene(parent=self)
        self.setScene(self.compositionScene)
        self.setAlignment((QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop))

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.verticalScrollBar().valueChanged.connect(self.scroll_changed)

    def scroll_changed(self, value):
        if self.headerWidget is not None:
            self.headerWidget.verticalScrollBar().setValue(value)

    def resize_scene(self):
        # w = self.viewport().width() / self.current_zoom * 2 + 25000
        #
        # self.scene().setSceneRect(QtCore.QRectF(self.scene().sceneRect().x(),
        #                                         self.scene().sceneRect().y(),
        #                                         w,
        #                                         self.scene().sceneRect().height()))

        # some items we do want to keep the same visual size. So we need to
        # inverse the effect of the zoom
        items_to_scale = [i for i in self.scene().items() if isinstance(i, _BaseItem)]

        for item in items_to_scale:
            item.counteract_zoom(1.0 / self.current_zoom)

    def fit_to(self, items=[]):
        if len(items) == 0:
            for item in self.scene().items():
                if isinstance(item, _BaseItem):
                    items.append(item)
        if len(items) > 0:
            max_x = items[0].pos().x() + items[0].rect().width()
            min_x = items[0].pos().x()
            max_y = items[0].pos().y()
            min_y = items[0].pos().y()
            for item in items:
                max_x = max(item.pos().x() + item.rect().width(), max_x)
                min_x = min(item.pos().x(), min_x)
                max_y = max(item.pos().y(), max_y)
                min_y = min(item.pos().y(), min_y)

            width = max_x - min_x
            # height = max_y - min_y

            center_x = (max_x + min_x) / 2
            center_y = (max_y + min_y) / 2

            # zoom_x = 1 / max(1, float(width) / self.viewport().width()) / self.current_zoom
            zoom_x = 1 / (float(width) / self.viewport().width()) / self.current_zoom
            # print zoom_x
            self.scale(zoom_x, 1)
            self.current_zoom = self.transform().m11()
            self.resize_scene()

            self.centerOn(QtCore.QPointF(center_x, center_y))

    def set_current_frame(self, frame):
        self.current_frame = frame
        point1 = self.mapToScene(QtCore.QPoint(0, 0))
        point2 = self.mapToScene(QtCore.QPoint(self.viewport().width(), self.viewport().height()))
        if not self.playing:
            self.scene().update(point1.x(),
                                point1.y(),
                                point2.x() - point1.x(),
                                point2.y() - point1.y())
        else:
            self.scene().update(frame - 2,
                                point1.y(),
                                frame + 1,
                                point2.y() - point1.y())

    def keyReleaseEvent(self, event):
        super(CompositionView, self).keyReleaseEvent(event)
        if event.text() == 'f':
            self.fit_to(self.scene().selectedItems())
        if event.text() == 'd':
            self.scene().mark_io_from_selected()

    def mousePressEvent(self, event):
        selected_items = self.scene().selectedItems()
        if event.button() == QtCore.Qt.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.panning = True
            self.prevPos = event.pos()
            self.prev_center = self.mapToScene(QtCore.QPoint(self.viewport().width() / 2, self.viewport().height() / 2))
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        elif event.button() == QtCore.Qt.RightButton:
            self.settingFrame = True
            pos = self.mapToScene(event.pos().x(), event.pos().y())
            # self.setFrame.emit(int(pos.x() + 1))
            set_frame(int(pos.x() + 1))
        super(CompositionView, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.MiddleButton:
            for item in selected_items:
                item.setSelected(True)

    def mouseMoveEvent(self, event):
        if self.panning:
            mouse_move = event.pos() - self.prevPos
            new_center = QtCore.QPointF(self.prev_center.x() - mouse_move.x() / self.current_zoom,
                                        self.prev_center.y() - mouse_move.y() / 1.0)
            self.centerOn(new_center)

        if self.settingFrame:
            pos = self.mapToScene(event.pos().x(), event.pos().y())
            # self.setFrame.emit(int(pos.x() + 1))
            set_frame(int(pos.x() + 1))

        super(CompositionView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, mouse_event):
        if self.panning:
            self.panning = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        if self.settingFrame:
            self.settingFrame = False
        super(CompositionView, self).mouseReleaseEvent(mouse_event)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def wheelEvent(self, event):
        scale_by = 1.0 + float(event.delta()) / 1000
        self.scale(scale_by, 1)
        self.current_zoom = self.transform().m11()

        self.resize_scene()

    def drawForeground(self, painter, rect):

        painter.setPen(QtGui.QPen(self.lineColor))

        frame_lines = []
        scale = max(int(1 / self.current_zoom / 0.05), 1)
        line_w = 1 * scale

        point1 = self.mapToScene(QtCore.QPoint(0, 0))
        point2 = self.mapToScene(QtCore.QPoint(self.viewport().width(), self.viewport().height()))

        for i in range(int(point1.x() / line_w), int(point2.x() / line_w)):
            frame_lines.append(QtCore.QLine(QtCore.QPoint(i * line_w, rect.y()),
                                            QtCore.QPoint(i * line_w, rect.y() + rect.height())))
        painter.drawLines(frame_lines)

        painter.setPen(QtGui.QPen(self.currentFrameLineColor))
        painter.setBrush(QtGui.QBrush(self.currentFrameRectColor))
        current_frame_rect = QtCore.QRectF(self.current_frame - 1,
                                           rect.y(),
                                           1.0,
                                           rect.height())
        painter.drawRect(current_frame_rect)
        # current_frame_line = QtCore.QLine(QtCore.QPoint(self.current_frame, rect.y()),
        #                            QtCore.QPoint(self.current_frame, rect.y() + rect.height())
        #                            )
        # painter.drawLine(current_frame_line)


class TrackHeadersScene(QtWidgets.QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(TrackHeadersScene, self).__init__(*args, **kwargs)

        self.composition = None

        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(58, 58, 58, 255)))

    def set_timeline(self, node):
        self.clear()
        self.composition = node
        self._adjust_scene_size()
        self._add_headers()

    def _adjust_scene_size(self):

        x, y, w, h = get_rect_from_view(self.composition)

        self.setSceneRect(
            0,
            0,
            HEADER_WIDTH,
            h
        )

    def _add_header(self, track, y_pos):
        scene_rect = self.sceneRect()
        rect = QtCore.QRectF(0, 0, scene_rect.width(), TRACK_HEIGHT)
        new_header = HeaderItem(track, rect)
        self.addItem(new_header)
        new_header.show_widget()
        new_header.setPos(scene_rect.x(), y_pos)

    def _add_headers(self):
        video_tracks_top = TIME_SLIDER_HEIGHT

        tracks = get_tracks_from_view(self.composition)

        for i, track in enumerate(tracks):
            self._add_header(track, video_tracks_top + i * (TRACK_HEIGHT + TRACK_GAP))


class TrackHeadersView(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(TrackHeadersView, self).__init__(*args, **kwargs)

        self.panning = False

        self.compWidget = None

        self.setFixedWidth(HEADER_WIDTH)

        self.trackHeadersScene = TrackHeadersScene(parent=self)
        self.setScene(self.trackHeadersScene)

        self.setAlignment((QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop))

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.horizontalScrollBar().hide()

        self.verticalScrollBar().valueChanged.connect(self.scroll_changed)

    def scroll_changed(self, value):
        if self.compWidget is not None:
            self.compWidget.verticalScrollBar().setValue(value)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.panning = True
            self.prevPos = event.pos()
            self.prev_center = self.mapToScene(QtCore.QPoint(self.viewport().width() / 2, self.viewport().height() / 2))
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        super(TrackHeadersView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            mouse_move = event.pos() - self.prevPos
            new_center = QtCore.QPointF(self.prev_center.x(),
                                        self.prev_center.y() - mouse_move.y() / 1.0)
            self.centerOn(new_center)
            return
        super(TrackHeadersView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, mouse_event):
        if self.panning:
            self.panning = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(TrackHeadersView, self).mouseReleaseEvent(mouse_event)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)


class Timeline(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Timeline, self).__init__(*args, **kwargs)
        self.node = None

        self.composition = CompositionView(parent=self)
        self.header = TrackHeadersView(parent=self)
        self.composition.headerWidget = self.header
        self.header.compWidget = self.composition
        master_layout = QtWidgets.QHBoxLayout()
        master_layout.addWidget(self.header)
        master_layout.addWidget(self.composition)
        master_layout.setSpacing(0)
        self.setLayout(master_layout)

    def set_timeline(self, node, auto_fit=True):
        self.node = node
        if is_timeline(node):
            self.composition.scene().set_timeline(node)
            self.header.scene().set_timeline(node)
            if auto_fit:
                self.composition.fit_to(list())

    def set_current_frame(self, frame):
        self.composition.set_current_frame(frame)


if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    window = Timeline()
    window.show()
    window.raise_()
    application.exec_()
