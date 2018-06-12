from PySide.QtCore import *
from PySide.QtGui import *
import types
import os
import math
import rv
import rv.qtutils
import rv.commands
from timeline_widget import Timeline

import pyside_test # need to get at the module itself

 
class PySideDockTest(rv.rvtypes.MinorMode):

    def __init__(self):
        rv.rvtypes.MinorMode.__init__(self)
        self.init("pyside_test", None, None, None)

        self.auto_update = True
        self.playing = False

        self.rvSessionObject = rv.qtutils.sessionWindow()
        self.dialog1 = QDockWidget('test', self.rvSessionObject)
        layout1 = QVBoxLayout()
        widget1 = QWidget()
        button1 = QPushButton('set timeline')
        # button1.clicked.connect(self.set_timeline)
        layout1.addWidget(button1)
        widget1.setLayout(layout1)
        self.dialog1.setWidget(widget1)
        self.rvSessionObject.addDockWidget(Qt.RightDockWidgetArea, self.dialog1)
        self.dialog1.hide()

        self.dialog2 = QDockWidget('Timeline', self.rvSessionObject)
        self.timeline = Timeline()
        self.timeline.composition.setFrame.connect(self.set_frame)
        self.dialog2.setWidget(self.timeline)
        self.rvSessionObject.addDockWidget(Qt.BottomDockWidgetArea, self.dialog2)

        rv.commands.bind('pyside_test', 'global', 'play-start', self.play_start(), '')
        rv.commands.bind('pyside_test', 'global', 'play-stop', self.play_stop(), '')
        rv.commands.bind('pyside_test', 'global', 'frame-changed', self.frame_changed(), '')
        rv.commands.bind('pyside_test', 'global', 'after-graph-view-change', self.set_timeline(), '')
        rv.commands.bind('pyside_test', 'global', 'graph-node-inputs-changed', self.inputs_changed(), '')
        rv.commands.bind('pyside_test', 'global', 'before-session-read', self.before_read_section(), '')
        rv.commands.bind('pyside_test', 'global', 'after-session-read', self.after_read_section(), '')

    def before_read_section(self):
        def bind(event):
            event.reject()
            self.auto_update = False
        return bind

    def after_read_section(self):
        def bind(event):
            event.reject()
            self.auto_update = True
        return bind

    def set_frame(self, frame):
        rv.commands.setFrame(frame)

    def set_timeline(self):
        def bind(event):
            event.reject()
            if not self.dialog2.isHidden():
                # print 'set timeline'
                self.timeline.set_timeline(rv.commands.viewNode())
        return bind

    def inputs_changed(self):
        def bind(event):
            event.reject()
            if not self.dialog2.isHidden():
                if self.auto_update:
                    current_view = rv.commands.viewNode()
                    if event.contents() == current_view:
                        # print 'refresh'
                        self.timeline.set_timeline(current_view, autoFit=False)
        return bind

    def get_frame(self):
        current_frame = rv.commands.frame()
        current_view = rv.commands.viewNode()
        print rv.commands.nodeRangeInfo(current_view)
        print rv.commands.nodeType(current_view)
        print rv.commands.nodeConnections(current_view)
        for node in rv.commands.nodesInGroup(current_view):
            print rv.commands.nodeType(node)
        sources = rv.commands.sourcesAtFrame(current_frame)
        for source in sources:
            print source, rv.commands.sourceMedia(source), rv.commands.nodeRangeInfo(source)

    def frame_changed(self):
        def bind(event):
            event.reject()
            if not self.dialog2.isHidden():
                self.timeline.set_current_frame(rv.commands.frame())
            # self.get_frame()
        return bind

    def play_start(self):
        def bind(event):
            event.reject()
            self.playing = True
            self.timeline.composition.playing = True
        return bind

    def play_stop(self):
        def bind(event):
            event.reject()
            self.playing = False
            self.timeline.composition.playing = False
            self.get_frame()
        return bind

    def activate(self):
        rv.rvtypes.MinorMode.activate(self)

    def deactivate(self):
        rv.rvtypes.MinorMode.deactivate(self)

def createMode():
    "Required to initialize the module. RV will call this function to create your mode."
    return PySideDockTest()
