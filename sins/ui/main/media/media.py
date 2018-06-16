# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/9/2018

import os
import sys
import time
from sins.module.sqt import *
from sins.ui.widgets.thumbnail_label import ThumbnailLabel
from sins.ui.widgets.tab.property_widget import PropertyWidget
from sins.ui.widgets.flow_layout import FlowLayout
from sins.test.test_res import TestMov
from sins.utils.res import resource
from sins.utils.python import get_name_data_from_class_or_instance
from sins.utils.log import get_logger, log_cost_time
from sins.db.models import *


logger = get_logger(__name__)

ThisFolder = os.path.dirname(__file__)

MEDIA_SIZE = [240, 165]
PLAYBUTTON_SIZE = 30
MEDIA_FONT_SIZE = 9


class MediaMainWindow(PropertyWidget):
    def __init__(self, parent=None):
        super(MediaMainWindow, self).__init__(parent)

        self.personId = None
        self.showList = None

        self.coreproperty_list = ['showList', 'personId']

        self.init_ui()

    def init_ui(self):
        self.filterTree = FilterTree()
        self.mediaGridWidget = MediaGridWidget()
        self.mediaArea = QScrollArea()
        self.mediaArea.setWidget(self.mediaGridWidget)
        self.mediaArea.setWidgetResizable(True)

        self.splitter = QSplitter()
        self.splitter.setHandleWidth(5)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.filterTree)
        self.splitter.addWidget(self.mediaArea)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        # self.splitter.setAutoFillBackground(True)
        # self.splitter.setOpaqueResize(False)

        self.masterLayout = QHBoxLayout()
        # self.masterLayout.addWidget(self.filterTree, 1)
        # self.masterLayout.addWidget(self.mediaArea, 3)
        self.masterLayout.addWidget(self.splitter)
        self.setLayout(self.masterLayout)
        self.masterLayout.setContentsMargins(0, 0, 0, 0)

        self.adjustSize()

        styleText = resource.get_style("media")
        self.setStyleSheet(styleText)

    def set_core_property(self, **kwargs):
        super(MediaMainWindow, self).set_core_property(**kwargs)
        if self.coreproperty_apply:
            logger.debug((self.__class__.__name__, kwargs))
            if 'personId' in kwargs and 'showList' not in kwargs:
                self.showList = []
                for project in Person.get(id=kwargs['personId']).projects:
                    self.showList.append(project.id)
            self.filterTree.set_show_list(self.showList)

    @log_cost_time
    def update_data(self):
        logger.debug((self.__class__.__name__))
        self.filterTree.load_data()


class FilterTreeItem(QTreeWidgetItem):
    def __init__(self, name=None, type=None, id=None, subtype=None, subId=None, parent=None):
        super(FilterTreeItem, self).__init__(parent)

        self.name = name
        self.type = type
        self.id = id
        self.subtype = subtype
        self.subId = subId

        self.setText(0, self.name)
        self.setToolTip(0, "type: %s\nid: %s" % (self.type, self.id))
        icon = type
        if subtype is not None:
            icon = subtype
        if icon is not None and hasattr(resource.icon, icon + '_B'):
            self.setIcon(0, resource.get_qicon(getattr(resource.icon, icon + '_B')))
        self.setSizeHint(0, QSize(100, 30))

    def children(self):
        children = []
        for i in range(self.childCount()):
            children.append(self.child(0))
        return children

    def clear_children(self):
        for i in range(self.childCount()):
            self.removeChild(self.child(0))


class FilterTree(QTreeWidget):
    def __init__(self):
        super(FilterTree, self).__init__()

        self.showList = []

        self.setHeaderHidden(True)
        # self.setAnimated(True)
        self.setColumnCount(1)
        self.setMaximumWidth(300)

        self.itemExpanded.connect(self.item_expanded)

    def set_show_list(self, showList):
        self.showList = showList

    def load_data(self):
        self.clear()
        self.load_recent()
        self.load_shows()

    def load_recent(self):
        recentsItem = FilterTreeItem("Recent")
        self.addTopLevelItem(recentsItem)
        for i in range(5):
            recentItem = FilterTreeItem("Recent%s" % i, type="Shot", id=i + 1)
            recentsItem.addChild(recentItem)

    def load_shows(self):
        for showid in self.showList:
            project = Project.get(id=showid)
            showItem = FilterTreeItem(project.code, type="Project", id=showid)
            self.addTopLevelItem(showItem)
            if len(self.showList) <= 1:
                showItem.setExpanded(True)
            assetsItem = FilterTreeItem("Assets", type="Project", id=showid, subtype="Asset")
            if project.assettypes.count() != 0:
                assetsItem.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            showItem.addChild(assetsItem)

            shotsItem = FilterTreeItem("Shots", type="Project", id=showid, subtype="Shot")
            if project.sequences.count() != 0:
                shotsItem.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            showItem.addChild(shotsItem)

    @log_cost_time
    def item_expanded(self, item):
        # print item.name, item.type, item.id, item.subtype
        logger.debug((item.name, item.type, item.id, item.subtype))
        QApplication.setOverrideCursor(Qt.WaitCursor)

        if item.type == 'Project' and item.subtype is not None:
            item.clear_children()
            children = None
            if item.subtype == 'Asset':
                children = AssetType.select().join(Project).where(Project.id == item.id)
            elif item.subtype == 'Shot':
                children = Sequence.select().join(Project).where(Project.id == item.id)
            for child in children:
                module_name, class_name = get_name_data_from_class_or_instance(child)
                childitem = FilterTreeItem(child.name, type=class_name, id=child.id)
                childitem.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                item.addChild(childitem)
                QCoreApplication.processEvents()
        if item.type == 'Sequence':
            item.clear_children()
            for child in Shot.select().join(Sequence).where(Sequence.id == item.id):
                childitem = FilterTreeItem(child.name, type='Shot', id=child.id)
                item.addChild(childitem)
                QCoreApplication.processEvents()
        if item.type == 'AssetType':
            item.clear_children()
            for child in Asset.select().join(AssetType).where(AssetType.id == item.id):
                childitem = FilterTreeItem(child.name, type='Asset', id=child.id)
                item.addChild(childitem)
                QCoreApplication.processEvents()

        QApplication.restoreOverrideCursor()

        
class MediaGridWidget(QWidget):
    def __init__(self):
        super(MediaGridWidget, self).__init__()
        self.setObjectName("MediaGridWidget")

        self.medias = []

        self.init_ui()
        self.load_version()
        self.load_prev()


    def init_ui(self):
        self.masterLayout = QVBoxLayout()
        # self.gridLayout = QGridLayout()
        self.gridLayout = FlowLayout(spacing=70)
        # print self.gridLayout.parent()
        # self.gridLayout.setContentsMargins(200, 200, 200, 200)
        self.setContentsMargins(50, 50, 0, 50)
        # self.gridLayout.setVerticalSpacing(100)
        # self.masterLayout.addSpacing(50)
        self.masterLayout.addLayout(self.gridLayout)
        self.masterLayout.addStretch()
        self.setLayout(self.masterLayout)


    def load_version(self, project=None, filter=None):
        num = 1
        for i in range(num):
            row = i / 5
            column = i % 5
            mediaWidget = MediaWidget()
            self.medias.append(mediaWidget)
            # self.gridLayout.addWidget(mediaWidget, row, column)
            self.gridLayout.addWidget(mediaWidget)

    def load_prev(self):
        # self.refreshPrevThread = RefreshPrevThread(len(self.medias))
        self.refreshPrevThread = RefreshPrevThread1(self.medias)
        # self.refreshPrevThread.test.connect(self.refresh_preview)
        self.refreshPrevThread.start()
        # for i in self.medias:
        #     i.load_info(0, 0)


    def refresh_preview(self, i):
        mediaWidget = self.medias[i]
        mediaWidget.load_info(0, 0)


class VersionNameWidget(QLabel):
    def __init__(self):
        super(VersionNameWidget, self).__init__()

        self.setObjectName('VersionNameWidget')

        self.playButton = PlayButton(self)
        self.versonLabel = QLabel("test_0920_cmp_comp_v001", self)
        self.versonLabel.setFont(QFont("Arial", MEDIA_FONT_SIZE))
        self.versonLabel.setFixedWidth(MEDIA_SIZE[0] - self.playButton.width())
        self.versonLabel.setAlignment(Qt.AlignCenter)

        self.bottomLay = QHBoxLayout()
        self.bottomLay.setAlignment(Qt.AlignLeft)
        self.bottomLay.addWidget(self.playButton)
        self.bottomLay.addWidget(self.versonLabel)
        self.bottomLay.setSpacing(0)
        self.bottomLay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.bottomLay)

        self.setFixedSize(MEDIA_SIZE[0] + 3, self.playButton.width() + 3)

        

class MediaWidget(QWidget):
    def __init__(self):
        super(MediaWidget, self).__init__()

        self.setObjectName("MediaWidget")
        self.init_ui()

        self.shotId = None
        self.versonId = None
        self.versonName = None
        self.versonPreviewFile = None
        self.cap = None

        self.create_signal()

    def init_ui(self):

        self.previewLabel = ThumbnailLabel(parent=self, dynamic=True, background='rgb(20, 35, 40)')
        self.versionNameWidget = VersionNameWidget()

        self.masterLayout = QVBoxLayout()
        self.masterLayout.setSpacing(0)
        self.masterLayout.addWidget(self.previewLabel)
        self.masterLayout.addSpacing(10)
        # self.masterLayout.addLayout(self.bottomLay)
        self.masterLayout.addWidget(self.versionNameWidget)
        self.masterLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.masterLayout)

        # self.setFixedSize(MEDIA_SIZE[0], MEDIA_SIZE[1] + 20)
        self.setMinimumWidth(MEDIA_SIZE[0])
        self.setFixedHeight(MEDIA_SIZE[1] + 25)

    def create_signal(self):
        # self.previewLabel.labelclicked.connect(self.open_shot_player)
        self.versionNameWidget.playButton.labelclicked.connect(self.open_shot_player)

    def load_info(self, shotId, versonId):
        self.shotId = shotId
        self.versonId = versonId
        # self.versonPreviewFile = TestMov("test3.mov")
        # self.versonPreviewFile = TestMov("test1080.mov")
        self.versonPreviewFile = TestMov("test.mp4")
        # self.versonPreviewFile = ""
        self.create_preview()

    def create_preview(self):
        # pass
        self.previewLabel.create_preview(self.versonPreviewFile)
        # if os.path.exists(self.versonPreviewFile):
        #     self.playButton.set_status(1)

    def open_shot_player(self):
        print "open_shot_player"


class PlayButton(QLabel):
    labelclicked = Signal()
    def __init__(self, parent=None):
        super(PlayButton, self).__init__(parent)

        self.status = 1

        self.status0Pixmap = resource.get_pixmap("button", "playButton_darkgray.png", scale=PLAYBUTTON_SIZE)
        self.status1Pixmap = resource.get_pixmap("button", "playButton_blue.png", scale=PLAYBUTTON_SIZE)

        self.setPixmap(self.status1Pixmap)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(PLAYBUTTON_SIZE + 7, PLAYBUTTON_SIZE + 7)

    def set_status(self, status=1):
        self.status = status
        if self.status:
            self.setPixmap(self.status1Pixmap)
        else:
            self.setPixmap(self.status0Pixmap)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, QMouseEvent):
        self.labelclicked.emit()


class RefreshPrevThread(QThread):
    test = Signal(int)
    def __init__(self, n):
        super(RefreshPrevThread, self).__init__()

        self.n = n

    def run(self):
        for i in range(self.n):
            self.test.emit(i)
            time.sleep(1)


class RefreshPrevThread1(QThread):
    def __init__(self, medias):
        super(RefreshPrevThread1, self).__init__()

        self.medias = medias

    def run(self):
        for i in self.medias:
            i.load_info(0, 0)


class TestWidget(QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()

        # self.setStyleSheet("""
        # QLabel#Back{
        # background:rgb(20, 20, 50);
        # border:1px solid white;
        # }
        # """)

        layout = QHBoxLayout()
        mediaWidget = MediaWidget()
        layout.addWidget(mediaWidget)
        self.setLayout(layout)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = MediaMainWindow()
    panel.set_core_property(showList=[1, 3])
    panel.update_data()
    # panel = TestWidget()
    # panel = VersionNameWidget()
    panel.show()
    app.exec_()