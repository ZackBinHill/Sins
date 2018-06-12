
from PySide import QtGui, QtCore
import os, shiboken
import rv
import rv.qtutils
import rv.commands
import rv.extra_commands
from version_scan import VersionScanner
import re
from timeline_widget import Timeline


import pyside_test # need to get at the module itself


def add_frame_range(filepath, frame_range):
    templist = filepath.split('.')
    templist[-2] = frame_range + templist[-2]
    return '.'.join(templist)


def remove_frame_range(filepath):
    templist = filepath.split('.')
    templist[-2] = '####'
    return '.'.join(templist)


def has_frame_range(filepath):
    match = re.match(r'.*\.(?P<range>\d*-\d*)####\.exr', filepath)
    if match:
        return True, match.group('range')
    else:
        return False, None


class VersionItem(QtGui.QListWidgetItem):
    def __init__(self, filePath, *args, **kwargs):
        super(VersionItem, self).__init__(*args, **kwargs)

        self.filePath = filePath
        if has_frame_range(filePath)[0]:
            filePath = remove_frame_range(filePath)
        self.setText(os.path.basename(filePath))
        # self.setSelected()


class VersionList(QtGui.QListWidget):
    def __init__(self, *args, **kwargs):
        super(VersionList, self).__init__(*args, **kwargs)

        self.currentFile = ''

    def set_current_file(self, filepath):
        is_seq = False
        if has_frame_range(filepath)[0]:
            is_seq = True
            frame_range = has_frame_range(filepath)[1]
        if filepath != self.currentFile:
            self.currentFile = filepath
            self.clear()
            versionScanner = VersionScanner()
            if is_seq:
                filepath_norange = remove_frame_range(filepath)
                versions = versionScanner.findVersionFiles(filepath_norange)
                for version in versions:
                    item = VersionItem(add_frame_range(version, frame_range))
                    self.addItem(item)
            else:
                versions = versionScanner.findVersionFiles(filepath)
                for version in versions:
                    item = VersionItem(version)
                    self.addItem(item)
        for index in range(self.count()):
            if self.item(index).filePath == filepath:
                self.item(index).setSelected(True)

    def wheelEvent(self, wheelevent):
        # QtGui.QWheelEvent.delta()
        lastIndex = self.selectedIndexes()[0].row()
        if wheelevent.delta() > 0:# version down
            if lastIndex == 0:
                lastIndex = self.count()
            self.item(lastIndex - 1).setSelected(True)
        else:  # version up
            if lastIndex == self.count() - 1:
                lastIndex = -1
            self.item(lastIndex + 1).setSelected(True)
        super(VersionList, self).wheelEvent(wheelevent)


class VersionWidget(QtGui.QWidget):
    itemChanged = QtCore.Signal(object)
    def __init__(self, *args, **kwargs):
        super(VersionWidget, self).__init__(*args, **kwargs)

        self.masterLayout = QtGui.QVBoxLayout()
        self.versionLists = []
        for i in range(10):
            versionListWidget = VersionList()
            self.masterLayout.addWidget(versionListWidget)
            versionListWidget.setVisible(False)
            versionListWidget.itemSelectionChanged.connect(self.item_select_changed)
            self.versionLists.append(versionListWidget)
        self.setLayout(self.masterLayout)

    def set_sources(self, sources):
        for versionList in self.versionLists:
            versionList.setVisible(False)
        for index, source in enumerate(sources):
            if index < 10:
                filepath = rv.commands.sourceMedia(source)[0]
                self.versionLists[index].set_current_file(filepath)
                self.versionLists[index].setVisible(True)

    def item_select_changed(self):
        self.itemChanged.emit(self.sender())


class PySideDockTest(rv.rvtypes.MinorMode):
    "A python mode example that uses PySide"

    def __init__(self):
        rv.rvtypes.MinorMode.__init__(self)
        self.init("pyside_test", None, None, None)

        self.playing = False

        self.rvSessionQObject = rv.qtutils.sessionWindow()
        self.dialog = QtGui.QDockWidget('test', self.rvSessionQObject)
        widget1 = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        button1 = QtGui.QPushButton('add source')
        button2 = QtGui.QPushButton('delete source')
        button3 = QtGui.QPushButton('get current frame')
        button4 = QtGui.QPushButton('add seq')
        button5 = QtGui.QPushButton('delete seq')
        button6 = QtGui.QPushButton('add stack')
        button7 = QtGui.QPushButton('delete stack')
        button8 = QtGui.QPushButton('add source to seq')
        button9 = QtGui.QPushButton('del source from seq')
        button10 = QtGui.QPushButton('add seq to stack(show)')
        button11 = QtGui.QPushButton('del seq from stack(hide)')
        button12 = QtGui.QPushButton('replace source')
        button1.clicked.connect(self.add_source)
        button2.clicked.connect(self.delete_source)
        button3.clicked.connect(self.get_frame)
        button4.clicked.connect(self.add_seq)
        button5.clicked.connect(self.del_seq)
        button6.clicked.connect(self.add_stack)
        button7.clicked.connect(self.del_stack)
        button8.clicked.connect(self.add_source_to_seq)
        button9.clicked.connect(self.del_source_from_seq)
        button10.clicked.connect(self.add_seq_to_stack)
        button11.clicked.connect(self.del_seq_from_stack)
        # button12.clicked.connect(self.replace_source)
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)
        layout.addWidget(button4)
        layout.addWidget(button5)
        layout.addWidget(button6)
        layout.addWidget(button7)
        layout.addWidget(button8)
        layout.addWidget(button9)
        layout.addWidget(button10)
        layout.addWidget(button11)
        layout.addWidget(button12)
        widget1.setLayout(layout)

        self.widget2 = VersionWidget()
        self.widget2.itemChanged.connect(self.item_select_changed)
        self.widget2.setMinimumWidth(200)

        masterWidget = QtGui.QWidget()
        masterLayout = QtGui.QVBoxLayout()
        # masterLayout.addWidget(widget1)
        masterLayout.addWidget(self.widget2)
        masterWidget.setLayout(masterLayout)

        self.dialog.setWidget(masterWidget)
        self.rvSessionQObject.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dialog)

        self.auto_update = True

        self.dialog2 = QtGui.QDockWidget('Timeline', self.rvSessionQObject)
        self.timeline = Timeline()
        self.timeline.composition.setFrame.connect(self.set_frame)
        self.dialog2.setWidget(self.timeline)
        self.rvSessionQObject.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dialog2)

        # rv.commands.bind('pyside_test', 'global', 'frame-changed', self.frame_changed(), '')
        # rv.commands.bind('pyside_test', 'global', 'new-source', self.new_source(), '')
        # rv.commands.bind('pyside_test', 'global', 'source-modified', self.source_modified(), '')
        # rv.commands.bind('pyside_test', 'global', 'media-relocated', self.media_relocated(), '')
        # rv.commands.bind('pyside_test', 'global', 'source-media-set', self.source_media_set(), '')
        # rv.commands.bind('pyside_test', 'global', 'new-node', self.new_node(), '')
        # rv.commands.bind('pyside_test', 'global', 'graph-new-node', self.graph_new_node(), '')
        # rv.commands.bind('pyside_test', 'global', 'new-in-point', self.new_in_point(), '')
        # rv.commands.bind('pyside_test', 'global', 'graph-node-inputs-changed', self.graph_node_inputs_changed(), '')
        # rv.commands.bind('pyside_test', 'global', 'range-changed', self.range_changed(), '')
        # rv.commands.bind('pyside_test', 'global', 'after-graph-view-change', self.after_graph_view_change, '')

        rv.commands.bind('pyside_test', 'global', 'play-start', self.play_start(), '')
        rv.commands.bind('pyside_test', 'global', 'play-stop', self.play_stop(), '')
        rv.commands.bind('pyside_test', 'global', 'frame-changed', self.frame_changed(), '')
        rv.commands.bind('pyside_test', 'global', 'after-graph-view-change', self.set_timeline(), '')
        rv.commands.bind('pyside_test', 'global', 'graph-node-inputs-changed', self.inputs_changed(), '')
        rv.commands.bind('pyside_test', 'global', 'before-session-read', self.before_read_section(), '')
        rv.commands.bind('pyside_test', 'global', 'after-session-read', self.after_read_section(), '')

    def add_source(self):
        file = '/isilon2/XAY.new/misc/dept/EDI/DailiesQT/MOV/QDQ_138_0010/QDQ_138_0010_cmp_v003.mov'
        print 'add source', file
        node = rv.commands.addSourceVerbose([file])

        file = '/isilon2/XAY.new/misc/dept/EDI/DailiesQT/EXR/QDQ_138_0010/QDQ_138_0010_lgt_v004/QDQ_138_0010_lgt_v004.preview.1000-1002####.exr'
        print 'add source', file
        node = rv.commands.addSourceVerbose([file])

        file = 'blank,start=1,end=21,fps=24.0.movieproc'
        print 'add source', file
        node = rv.commands.addSourceVerbose([file])
        group = rv.commands.nodeGroup(node)
        rv.commands.setViewNode(group)

    def delete_source(self):
        file = '/job/HOME/xinghuan/temp/render_test/testmov_png .mov'
        print 'delete source', file
        # rv.commands.deleteNode(self.gapnode)
        for s in rv.commands.nodesOfType('RVFileSource'):
            group = rv.commands.nodeGroup(s)
            print group, rv.extra_commands.uiName(group)

    def get_frame(self):
        if not self.playing:
            current_frame = rv.commands.frame()
            # print 'current_frame:', current_frame
            current_view = rv.commands.viewNode()
            # print 'current view:', current_view, rv.commands.nodeType(current_view)
            # print 'connects:', rv.commands.nodeConnections(current_view)
            current_sources = rv.commands.sourcesAtFrame(current_frame)
            for source in current_sources:
                # print source, rv.commands.sourceMedia(source), rv.commands.nodeRangeInfo(source)
                self.widget2.set_sources(current_sources)

    def add_seq(self):
        n = rv.commands.newNode('RVSequenceGroup', 'Video_1')
        print n, rv.extra_commands.uiName(n)

    def del_seq(self):
        rv.commands.deleteNode('Video_1')

    def add_stack(self):
        n = rv.commands.newNode('RVStackGroup', 'Stack_0')
        print n
        rv.commands.setViewNode(n)
        rv.commands.setIntProperty('#RVStack.mode.alignStartFrames', [1])

    def del_stack(self):
        pass

    def add_source_to_seq(self):
        pass

    def del_source_from_seq(self):
        pass

    def add_seq_to_stack(self):
        pass

    def del_seq_from_stack(self):
        pass

    def replace_source(self, oldfile, newfile):
        current_frame = rv.commands.frame()
        current_sources = rv.commands.sourcesAtFrame(current_frame)
        for source in current_sources:
            print 'before replace:', source, rv.commands.sourceMedia(source), rv.commands.nodeRangeInfo(source)
            if rv.commands.sourceMedia(source)[0] == oldfile:
                rv.commands.setSourceMedia(source, [newfile])
                print 'after replace:', source, rv.commands.sourceMedia(source), rv.commands.nodeRangeInfo(source)
                # print 'affect tracks:', rv.commands.nodeConnections(rv.commands.nodeGroup(source))[1]
                for node in rv.commands.nodeConnections(rv.commands.nodeGroup(source))[1]:
                    # print node, rv.extra_commands.uiName(node)
                    self.timeline.composition.scene().rebuild_track(node)

    # def frame_changed(self):
    #     def test(event):
    #         self.get_frame()
    #     return test

    def item_select_changed(self, sender):
        versionList = sender
        if len(versionList.selectedItems()) != 0:
            item = versionList.selectedItems()[0]
            # print item.filePath, versionList.currentFile
            if item.filePath != versionList.currentFile:
                self.replace_source(versionList.currentFile, item.filePath)
                versionList.currentFile = item.filePath
                self.get_frame()

    def new_source(self):
        def test(event):
            print 'new_source'
            contents = event.contents()
            print 'contents:', contents
        return test

    def source_modified(self):
        def test(event):
            print 'source_modified'
            contents = event.contents()
            print 'contents:', contents
        return test

    def media_relocated(self):
        def test(event):
            print 'media_relocated'
            contents = event.contents()
            print 'contents:', contents
        return test

    def source_media_set(self):
        def test(event):
            print 'source_media_set'
            contents = event.contents()
            print 'contents:', contents
        return test

    def new_node(self):
        def test(event):
            print 'new_node'
        return test

    def graph_new_node(self):
        def test(event):
            print 'graph_new_node'
        return test

    def new_in_point(self):
        def test(event):
            print 'new_in_point'
        return test

    def graph_node_inputs_changed(self):
        def test(event):
            print 'graph_node_inputs_changed'
        return test

    def range_changed(self):
        def test(event):
            event.reject()
            print 'range_changed'
        return test

    def after_graph_view_change(self, event):
        # def test(event):
        event.reject()
        print 'after_graph_view_change'
        contents = event.contents()
        print 'contents:', contents
        # return test

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
            if self.auto_update:
                self.timeline.set_timeline(rv.commands.viewNode())
        return bind

    def inputs_changed(self):
        def bind(event):
            event.reject()
            if self.auto_update:
                current_view = rv.commands.viewNode()
                if event.contents() == current_view:
                    # print 'refresh'
                    self.timeline.set_timeline(current_view, autoFit=False)
                    self.get_frame()
        return bind

    def frame_changed(self):
        def bind(event):
            event.reject()
            self.timeline.set_current_frame(rv.commands.frame())
            self.get_frame()
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
        print __name__, os.path.abspath(__file__)
        self.dialog.show()
        # self.dialog2.show()

    def deactivate(self):
        rv.rvtypes.MinorMode.deactivate(self)
        self.dialog.hide()
        # self.dialog2.hide()

def createMode():
    "Required to initialize the module. RV will call this function to create your mode."
    return PySideDockTest()

