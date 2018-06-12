import os
os.environ['BQT_BINDING'] = 'PySide'
# from PySide import QtGui, QtCore
from BQt import QtWidgets, QtGui, QtCore
import re
import rv
import rv.qtutils
import rv.commands
import rv.extra_commands
import rv.rvui
from version_scan import VersionScanner
from timeline_widget import Timeline


import pyside_test # need to get at the module itself

PIPELINE_STEPS = ['cmp', 'lgt', 'lay', 'ani', 'env', 'dmt', 'efx', 'editref']
FILE_TYPES = ['mov', 'exr']
HANDLE_FRAMES = 8


def add_frame_range(filepath, frame_range=None, cutin=None, cutout=None):
    templist = filepath.split('.')
    if frame_range is not None:
        templist[-2] = frame_range + templist[-2]
    if cutin is not None and cutout is not None:
        templist[-2] = '{}-{}'.format(cutin - HANDLE_FRAMES - 1, cutout + HANDLE_FRAMES) + templist[-2]
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


def convert_ext(from_filepath, cutin=None, cutout=None):
    name, current_type = os.path.splitext(from_filepath)
    if current_type == '.mov':
        filepath = from_filepath.replace('MOV', 'EXR').replace('.mov', '.preview.####.exr')
        templist = filepath.split('/')
        templist.insert(-1, templist[-1].replace('.preview.####.exr', ''))
        filepath = add_frame_range('/'.join(templist),
                                   cutin=cutin,
                                   cutout=cutout)
        # print templist
        return filepath
    if current_type == '.exr':
        filepath = remove_frame_range(from_filepath).replace('EXR', 'MOV').replace('.preview.####.exr', '.mov')
        templist = filepath.split('/')
        templist.remove(templist[-2])
        filepath = '/'.join(templist)
        # print templist
        return filepath


class VersionItem(QtWidgets.QListWidgetItem):
    def __init__(self, file_path, *args, **kwargs):
        super(VersionItem, self).__init__(*args, **kwargs)

        self.filePath = file_path
        if has_frame_range(file_path)[0]:
            file_path = remove_frame_range(file_path)
        self.setText(os.path.basename(file_path))
        # self.setSelected()
        # self.setHidden()


class VersionList(QtWidgets.QListWidget):
    def __init__(self, *args, **kwargs):
        super(VersionList, self).__init__(*args, **kwargs)

        self.currentFile = ''
        self.cutin = None
        self.cutout = None
        self.versions = []
        self.versionNum = None
        self.create_context_menu()

    def set_current_file(self, filepath, cutin=None, cutout=None):
        if filepath != self.currentFile:
            self.currentFile = filepath
            self.cutin = cutin
            self.cutout = cutout
            self.clear()
            self.add_items(filepath)

        for index in range(self.count()):
            if self.item(index).filePath == filepath:
                self.item(index).setSelected(True)

    def refresh_list(self):
        self.clear()
        self.add_items(self.currentFile)
        for index in range(self.count()):
            if self.item(index).filePath == self.currentFile:
                self.item(index).setSelected(True)

    def add_items(self, filepath):
        is_seq = False
        if has_frame_range(filepath)[0]:
            is_seq = True
            frame_range = has_frame_range(filepath)[1]

        version_scanner = VersionScanner()
        if is_seq:
            filepath_norange = remove_frame_range(filepath)
            self.versions = version_scanner.findVersionFiles(filepath_norange)
            self.versions.sort(reverse=True)
            if self.versionNum:
                self.versions = self.versions[:self.versionNum]
            for version in self.versions:
                item = VersionItem(add_frame_range(version, frame_range=frame_range))
                self.addItem(item)
        else:
            self.versions = version_scanner.findVersionFiles(filepath)
            self.versions.sort(reverse=True)
            if self.versionNum:
                self.versions = self.versions[:self.versionNum]
            for version in self.versions:
                item = VersionItem(version)
                self.addItem(item)

    def wheelEvent(self, wheelevent):
        # QtWidgets.QWheelEvent.delta()
        last_index = self.selectedIndexes()[0].row() if len(self.selectedIndexes()) > 0 else 0
        if wheelevent.delta() > 0:# version down
            if last_index == 0:
                last_index = self.count()
            self.item(last_index - 1).setSelected(True)
        else:  # version up
            if last_index == self.count() - 1:
                last_index = -1
            self.item(last_index + 1).setSelected(True)
        super(VersionList, self).wheelEvent(wheelevent)

    def create_context_menu(self):
        self.menu = QtWidgets.QMenu(self)
        self.addStepMenu = QtWidgets.QMenu('Add pipeline step', self)
        self.addTypeMenu = QtWidgets.QMenu('Add file type', self)
        for step in PIPELINE_STEPS:
            action = QtWidgets.QAction(step, self.addStepMenu)
            action.triggered.connect(self.add_new_step_to_list)
            self.addStepMenu.addAction(action)
        for type in FILE_TYPES:
            action = QtWidgets.QAction(type, self.addTypeMenu)
            action.triggered.connect(self.add_new_type_to_list)
            self.addTypeMenu.addAction(action)
        self.menu.addMenu(self.addStepMenu)
        self.menu.addMenu(self.addTypeMenu)

    def contextMenuEvent(self, event):
        super(VersionList, self).contextMenuEvent(event)
        self.menu.move(QtGui.QCursor().pos())
        self.menu.show()

    def add_new_step_to_list(self):
        # print self.sender().text()
        current_step = None
        for step in PIPELINE_STEPS:
            if self.currentFile.find(step) != -1:
                current_step = step
                break
        if current_step:
            version_scanner = VersionScanner()
            filepath = self.currentFile.replace(current_step, self.sender().text())
            # print filepath
            self.add_items(filepath)

    def add_new_type_to_list(self):
        name, current_type = os.path.splitext(self.currentFile)
        if current_type == '.mov' and self.sender().text() == 'exr':
            filepath = convert_ext(self.currentFile, cutin=self.cutin, cutout=self.cutout)
            print filepath
            self.add_items(filepath)
        elif current_type == '.exr' and self.sender().text() == 'mov':
            filepath = convert_ext(self.currentFile)
            print filepath
            self.add_items(filepath)

    def set_version_num(self, num):
        self.versionNum = num
        # print self.count()
        for index in range(self.count()):
            if index >= num:
                self.item(index).setHidden(True)
            else:
                self.item(index).setHidden(False)


class VersionWidget(QtWidgets.QWidget):
    itemChanged = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(VersionWidget, self).__init__(*args, **kwargs)

        self.masterLayout = QtWidgets.QVBoxLayout()
        self.layout1 = QtWidgets.QHBoxLayout()
        self.versionNumEdit = QtWidgets.QLineEdit()
        self.versionNumEdit.setPlaceholderText('Display Version Number:')
        self.versionNumEdit.setText(str(rv.commands.readSettings('Dailies', 'versionNum', 5)))
        self.versionNumEdit.editingFinished.connect(self.change_version_number)
        self.refreshButton = QtWidgets.QPushButton('Refresh')
        self.refreshButton.clicked.connect(self.refresh_clicked)
        self.layout1.addWidget(self.versionNumEdit)
        self.layout1.addWidget(self.refreshButton)
        self.masterLayout.addLayout(self.layout1)
        self.versionLists = []
        for i in range(10):
            version_list_widget = VersionList()
            self.masterLayout.addWidget(version_list_widget)
            version_list_widget.setVisible(False)
            version_list_widget.itemSelectionChanged.connect(self.item_select_changed)
            version_list_widget.set_version_num(int(self.versionNumEdit.text()))
            self.versionLists.append(version_list_widget)
        self.setLayout(self.masterLayout)

    def set_sources(self, sources):
        for versionList in self.versionLists:
            versionList.setVisible(False)
        for index, source in enumerate(sources):
            if index < 10:
                filepath = rv.commands.sourceMedia(source)[0]
                range_info = rv.commands.nodeRangeInfo(source)
                self.versionLists[index].set_current_file(filepath,
                                                          cutin=range_info['cutIn'],
                                                          cutout=range_info['cutOut'])
                self.versionLists[index].setVisible(True)

    def item_select_changed(self):
        self.itemChanged.emit(self.sender())

    def change_version_number(self):
        try:
            version_num = int(self.versionNumEdit.text())
            # print version_num
            for versionList in self.versionLists:
                if versionList.isVisible():
                    versionList.set_version_num(version_num)
            rv.commands.writeSettings('Dailies', 'versionNum', version_num)
        except:
            pass

    def refresh_clicked(self):
        for versionList in self.versionLists:
            if versionList.isVisible():
                versionList.refresh_list()


class PySideDockTest(rv.rvtypes.MinorMode):
    def __init__(self):
        rv.rvtypes.MinorMode.__init__(self)
        # self.init("pyside_test", [("key-down--s", self.go_to_shot_edit, ""),], None, None)
        self.init("pyside_test", None, None, None)

        self.playing = False

        self.rvSessionQObject = rv.qtutils.sessionWindow()
        self.sessionGLView = rv.qtutils.sessionGLView()
        self.toShotEdit = QtWidgets.QLineEdit(self.sessionGLView)
        self.toShotLabel = QtWidgets.QLabel('Go To Shot:', self.toShotEdit)
        self.toShotLabel.setFixedHeight(self.toShotEdit.height())
        self.toShotEdit.hide()
        self.toShotEdit.setTextMargins(80, 0, 0, 0)
        self.toShotEdit.setStyleSheet("""
        QLineEdit{
            border:none;
        }
        QLabel{
            background:transparent;
        }
        """)
        # self.toShotEdit.editingFinished.connect(self.go_to_shot)

        self.dialog = QtWidgets.QDockWidget('version', self.rvSessionQObject)
        widget1 = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        button1 = QtWidgets.QPushButton('add source')
        button2 = QtWidgets.QPushButton('delete source')
        button3 = QtWidgets.QPushButton('get current frame')
        button4 = QtWidgets.QPushButton('add seq')
        button5 = QtWidgets.QPushButton('delete seq')
        button6 = QtWidgets.QPushButton('add stack')
        button7 = QtWidgets.QPushButton('delete stack')
        button8 = QtWidgets.QPushButton('add source to seq')
        button9 = QtWidgets.QPushButton('del source from seq')
        button10 = QtWidgets.QPushButton('add seq to stack(show)')
        button11 = QtWidgets.QPushButton('del seq from stack(hide)')
        button12 = QtWidgets.QPushButton('replace source')
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

        self.versionWidget = VersionWidget()
        self.versionWidget.itemChanged.connect(self.item_select_changed)
        self.versionWidget.setMinimumWidth(200)

        master_widget = QtWidgets.QWidget()
        master_layout = QtWidgets.QVBoxLayout()
        # master_layout.addWidget(widget1)
        master_layout.addWidget(self.versionWidget)
        master_widget.setLayout(master_layout)

        self.dialog.setWidget(master_widget)
        self.rvSessionQObject.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dialog)

        self.auto_update = True

        self.dialog2 = QtWidgets.QDockWidget('Timeline', self.rvSessionQObject)
        self.timeline = Timeline()
        # self.timeline.composition.setFrame.connect(self.set_frame)
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
        rv.commands.bind('pyside_test', 'global', 'after-graph-view-change', self.view_changed, '')
        rv.commands.bind('pyside_test', 'global', 'graph-node-inputs-changed', self.inputs_changed(), '')
        rv.commands.bind('pyside_test', 'global', 'before-session-read', self.before_read_section(), '')
        rv.commands.bind('pyside_test', 'global', 'after-session-read', self.after_read_section(), '')
        rv.commands.bind('pyside_test', 'global', 'key-down--s', self.go_to_shot_edit, '')

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
                self.versionWidget.set_sources(current_sources)

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
            # print 'before replace:', source, rv.commands.sourceMedia(source), rv.commands.nodeRangeInfo(source)
            if rv.commands.sourceMedia(source)[0] == oldfile:
                rv.commands.setSourceMedia(source, [newfile])
                # print 'after replace:', source, rv.commands.sourceMedia(source), rv.commands.nodeRangeInfo(source)
                # print 'affect tracks:', rv.commands.nodeConnections(rv.commands.nodeGroup(source))[1]
                for node in rv.commands.nodeConnections(rv.commands.nodeGroup(source))[1]:
                    # print node, rv.extra_commands.uiName(node)
                    self.timeline.composition.scene().rebuild_track(node)

    # def frame_changed(self):
    #     def test(event):
    #         self.get_frame()
    #     return test

    def item_select_changed(self, sender):
        version_list = sender
        if len(version_list.selectedItems()) != 0:
            item = version_list.selectedItems()[0]
            # print item.filePath, version_list.currentFile
            if item.filePath != version_list.currentFile:
                self.replace_source(version_list.currentFile, item.filePath)
                version_list.currentFile = item.filePath
                # self.get_frame()

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

    # def set_frame(self, frame):
    #     rv.commands.setFrame(frame)

    def set_timeline(self):
        # def bind(event):
        #     event.reject()
        if self.auto_update:
            self.timeline.set_timeline(rv.commands.viewNode())
        # return bind

    def view_changed(self, event):
        event.reject()
        self.set_timeline()
        current_view = rv.commands.viewNode()
        if rv.commands.nodeType(current_view) == 'RVStackGroup':
            rv.commands.setStringProperty("#RVStack.composite.type", ["topmost"])
            rv.commands.setIntProperty("#RVStack.mode.alignStartFrames", [1])
            # rv.extra_commands.set("#RVStack.composite.type", "topmost")

    def inputs_changed(self):
        def bind(event):
            event.reject()
            if self.auto_update:
                current_view = rv.commands.viewNode()
                if event.contents() == current_view:
                    # print 'refresh'
                    self.timeline.set_timeline(current_view, auto_fit=False)
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

    def go_to_shot_edit(self, event):
        if self.toShotEdit.isHidden():
            self.toShotEdit.move(0, self.sessionGLView.height() - self.toShotEdit.height())
            self.toShotEdit.clear()
            self.toShotEdit.show()
            self.toShotEdit.setFocus()
            self.toShotEdit.editingFinished.connect(self.go_to_shot)

    def go_to_shot(self):
        self.toShotEdit.editingFinished.disconnect(self.go_to_shot)
        shot = self.toShotEdit.text()
        self.toShotEdit.hide()
        self.sessionGLView.setFocus()

        node = rv.commands.viewNode()
        node_type = rv.commands.nodeType(node)
        if node_type == 'RVSequenceGroup':
            self.view_shot_in_seq(node, shot)
        elif node_type in ['RVSwitchGroup', 'RVStackGroup']:
            for input_node in rv.commands.nodeConnections(node)[0]:
                if rv.commands.nodeType(input_node) == 'RVSequenceGroup':
                    result = self.view_shot_in_seq(input_node, shot)
                    if result:
                        break

    def view_shot_in_seq(self, seq, shot):
        frame = 1
        for input_node in rv.commands.nodeConnections(seq)[0]:
            input_name = rv.extra_commands.uiName(input_node)
            if input_name.find(shot) != -1:
                rv.commands.setFrame(frame)
                return True
            else:
                noderange = rv.commands.nodeRangeInfo(input_node)
                duration = noderange['cutOut'] - noderange['cutIn'] + 1
                frame += duration
        return False

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
