# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/9/2018

import sys
from sins.module.sqt import *
from sins.ui.widgets.label import ThumbnailLabel
from sins.ui.widgets.tab.property_widget import PropertyWidget
from sins.ui.widgets.flow_layout import FlowLayout
from sins.ui.utils import get_text_wh
from sins.utils.python import get_name_data_from_class_or_instance
from sins.utils.log import log_cost_time
from sins.db.models import *
from sins.db.permission import get_permission_projects


logger = get_logger(__name__)

MEDIA_SIZE = [240, 165]
PLAYBUTTON_SIZE = 30
MEDIA_FONT_SIZE = 9
VERSION_NAME_MAX_LENGTH = 200


class MediaMainWindow(PropertyWidget):
    def __init__(self, parent=None):
        super(MediaMainWindow, self).__init__(parent)

        self.personId = None
        self.showList = None

        self.coreproperty_list = ['showList', 'personId']

        self.init_ui()

        self.entityTree.itemSelectionChanged.connect(self.entity_select_changed)

    def init_ui(self):
        self.entityTree = EntityTree()
        self.mediaGridWidget = MediaGridWidget()
        self.mediaArea = QScrollArea()
        self.mediaArea.setWidget(self.mediaGridWidget)
        self.mediaArea.setWidgetResizable(True)

        self.splitter = QSplitter()
        self.splitter.setHandleWidth(5)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.entityTree)
        self.splitter.addWidget(self.mediaArea)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        # self.splitter.setAutoFillBackground(True)
        # self.splitter.setOpaqueResize(False)

        self.masterLayout = QHBoxLayout()
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
                projects = get_permission_projects(Person.get(id=kwargs['personId']))
                prefetch(projects, Sequence, AssetType)
                for project in projects:
                    self.showList.append(project)
            self.entityTree.set_show_list(self.showList)

    @log_cost_time
    def update_data(self):
        logger.debug((self.__class__.__name__))
        self.entityTree.load_data()

    def entity_select_changed(self):
        selected_items = self.entityTree.selectedItems()
        if len(selected_items) > 0:
            selected_item = selected_items[0]
            entity = selected_item.entity
            versions = entity.versions
            if selected_item.sub_type == 'Shot':
                versions = versions.where(Version.shot.is_null(False))
            elif selected_item.sub_type == 'Asset':
                versions = versions.where(Version.asset.is_null(False))
            print selected_item.type, selected_item.id, selected_item.sub_id
            print versions, versions.count()
            versions = versions.where(Version.uploaded_movie.is_null(False))
            versions = versions.limit(5)

            self.mediaGridWidget.clear_versions()
            self.mediaGridWidget.load_version(versions)
            self.mediaGridWidget.load_prev()


class EntityTreeItem(QTreeWidgetItem):
    def __init__(self,
                 name=None,
                 entity=None,
                 type=None,
                 id=None,
                 sub_type=None,
                 sub_id=None,
                 parent=None):
        super(EntityTreeItem, self).__init__(parent)

        self.name = name
        self.entity = entity
        self.type = type
        self.id = id
        self.sub_type = sub_type
        self.sub_id = sub_id

        self.setText(0, self.name)
        self.setToolTip(0, "type: %s\nid: %s" % (self.type, self.id))
        icon = type
        if sub_type is not None:
            icon = sub_type
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


class EntityTree(QTreeWidget):
    def __init__(self):
        super(EntityTree, self).__init__()

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
        recentsItem = EntityTreeItem("Recent")
        self.addTopLevelItem(recentsItem)
        for i in range(5):
            recentItem = EntityTreeItem("Recent%s" % i, type="Shot", id=i + 1)
            recentsItem.addChild(recentItem)

    def load_shows(self):
        for show in self.showList:
            if isinstance(show, int):
                project = Project.get(id=show)
            else:
                project = show
            showItem = EntityTreeItem(project.code, entity=project, type="Project", id=project.id)
            self.addTopLevelItem(showItem)
            if len(self.showList) <= 1:
                showItem.setExpanded(True)
            assetsItem = EntityTreeItem("Assets", entity=project, type="Project", id=project.id, sub_type="Asset")
            asset_types = project.assettypes
            asset_types_count = len(asset_types) if isinstance(asset_types, list) else asset_types.count()
            if asset_types_count != 0:
                assetsItem.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            showItem.addChild(assetsItem)

            shotsItem = EntityTreeItem("Shots", entity=project, type="Project", id=project.id, sub_type="Shot")
            sequences = project.sequences
            sequences_count = len(sequences) if isinstance(sequences, list) else sequences.count()
            if sequences_count != 0:
                shotsItem.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            showItem.addChild(shotsItem)

    @log_cost_time
    def item_expanded(self, item):
        # print item.name, item.type, item.id, item.sub_type
        logger.debug((item.name, item.type, item.id, item.sub_type))
        QApplication.setOverrideCursor(Qt.WaitCursor)

        if item.type == 'Project' and item.sub_type is not None:
            item.clear_children()
            children = None
            if item.sub_type == 'Asset':
                children = AssetType.select().join(Project).where(Project.id == item.id)
            elif item.sub_type == 'Shot':
                children = Sequence.select().join(Project).where(Project.id == item.id)
            for child in children:
                module_name, class_name = get_name_data_from_class_or_instance(child)
                childitem = EntityTreeItem(child.name, entity=child, type=class_name, id=child.id)
                childitem.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                item.addChild(childitem)
                QCoreApplication.processEvents()

        if item.type in ['AssetType', 'Sequence']:
            item.clear_children()
            for child in item.entity.children:
                childitem = EntityTreeItem(child.name, entity=child, type=child.__class__.__name__, id=child.id)
                item.addChild(childitem)
                QCoreApplication.processEvents()

        QApplication.restoreOverrideCursor()

        
class MediaGridWidget(QWidget):
    def __init__(self):
        super(MediaGridWidget, self).__init__()
        self.setObjectName("MediaGridWidget")

        self.medias = []

        self.init_ui()

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

    def clear_versions(self):
        self.clear_layout(self.gridLayout)

    def clear_layout(self, layout):
        if layout != None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def load_version(self, versions):
        for v in versions:
            mediaWidget = MediaWidget(verson=v)
            self.medias.append(mediaWidget)
            self.gridLayout.addWidget(mediaWidget)
            QCoreApplication.processEvents()

    def load_prev(self):
        # self.refreshPrevThread = RefreshPrevThread(len(self.medias))
        self.refreshPrevThread = RefreshPrevThread1(self.medias)
        # self.refreshPrevThread.test.connect(self.refresh_preview)
        self.refreshPrevThread.start()
        # for i in self.medias:
        #     i.load_info(0, 0)

    def refresh_preview(self, i):
        mediaWidget = self.medias[i]
        mediaWidget.load_info()


class VersionNameWidget(QLabel):
    def __init__(self, version_name=''):
        super(VersionNameWidget, self).__init__()

        self.setObjectName('VersionNameWidget')

        self.playButton = PlayButton(self)

        font = QFont("Arial", MEDIA_FONT_SIZE)
        name_width, _ = get_text_wh(version_name, font)
        if name_width > VERSION_NAME_MAX_LENGTH:
            temp_name1 = version_name[:10]
            temp_name2 = version_name[-10:]
            version_name = temp_name1 + '...' + temp_name2

        self.versonLabel = QLabel(version_name, self)
        self.versonLabel.setFont(font)
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
    def __init__(self, verson=None):
        super(MediaWidget, self).__init__()

        self.setObjectName("MediaWidget")

        self.verson = verson
        self.versonName = verson.name if verson is not None else ''
        self.versonPreviewFile = None
        self.cap = None

        self.init_ui()

        self.create_signal()

    def init_ui(self):

        self.previewLabel = ThumbnailLabel(parent=self,
                                           dynamic=True,
                                           background='rgb(20, 35, 40)')
        self.versionNameWidget = VersionNameWidget(self.versonName)

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

    def load_info(self):
        if self.verson is not None:
            uploaded_movie = self.verson.uploaded_movie
            if uploaded_movie is not None:
                if os.path.exists(uploaded_movie.host_path):
                    self.versonPreviewFile = uploaded_movie.host_path
                    self.create_preview()
                else:
                    logger.warning('version uploaded_movie file not exist')
            else:
                logger.debug('version no uploaded_movie')

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
            i.load_info()


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
    # panel.set_core_property(showList=[1, 3])
    panel.set_core_property(personId=1)
    panel.update_data()
    # panel = TestWidget()
    # panel = VersionNameWidget()
    panel.show()
    app.exec_()