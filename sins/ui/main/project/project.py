# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/10/2018

import os
import sys
from sins.module.sqt import *
from sins.db.models import *
from sins.ui.main.media.media import MediaMainWindow
from shots.shots import ShotMainWindow
from sins.ui.widgets.tab.custom_tab import CustomTabWindow, ProjectTabButton, MediaTabButton
from sins.ui.widgets.tab.property_widget import PropertyWidget
from sins.utils.res import resource
from sins.utils.log import get_logger


logger = get_logger(__name__)


PROJECT_PAGES = [
    "Sequences",
    "Assettypes",
    "Persons",
    "Departments",
    "Groups",
    "PermissionGroups",
    "Files",
    "Tasks",
    "Timelogs",
    "Tags",
    "Status",
    "PipelineSteps",
    "Playlists",
]


class ProjectMainWindow(CustomTabWindow, PropertyWidget):
    def __init__(self, *args, **kwargs):
        super(ProjectMainWindow, self).__init__(*args, **kwargs)

        self.showId = None
        self.showName = None

        self.coreproperty_list = ['showId', 'showName']

        self.init_ui()

    def init_ui(self):

        self.projectLabel = QLabel("UNKNOW")
        self.projectLabel.setObjectName("projectLabel")
        self.projectLabel.setFont(QFont("Roman times", 12, QFont.Bold))
        self.projectLabel.setFixedHeight(35)
        self.projectLabel.setMinimumWidth(70)
        self.projectLabel.setAlignment(Qt.AlignCenter)
        self.projectLabel.setContentsMargins(10, 0, 10, 0)

        self.mediaWindow = MediaMainWindow()
        self.shotsWindow = ShotMainWindow(parent=self)

        self.add_head(self.projectLabel)

        self.add_tab(QLabel("Overview"), ProjectTabButton("Overview"), "Overview")
        self.add_tab(QLabel("Detail"), ProjectTabButton("Detail"), "Detail")
        self.add_tab(QLabel("Assets"), ProjectTabButton("Assets"), "Assets")
        self.add_tab(QLabel("Versons"), ProjectTabButton("Versons"), "Versons")
        self.add_tab(QLabel("Notes"), ProjectTabButton("Notes"), "Notes")
        self.shotsButton = ProjectTabButton("Shots")
        self.shotsButton.defaultPage = [{"pagename": 'All', "coreproperty": {}}]
        # self.shotsButton.set_core_property({'showId': 1})
        self.add_tab(self.shotsWindow, self.shotsButton, "Shots")
        self.add_tab(self.mediaWindow, MediaTabButton("Media"), "Media")

        self.add_tab(QLabel("Sequences"), ProjectTabButton("Sequences", hide=True), "Sequences")
        self.add_tab(QLabel("Assettypes"), ProjectTabButton("Assettypes", hide=True), "Assettypes")
        self.add_tab(QLabel("Persons"), ProjectTabButton("Persons", hide=True), "Persons")
        self.add_tab(QLabel("Departments"), ProjectTabButton("Departments", hide=True), "Departments")
        self.add_tab(QLabel("Groups"), ProjectTabButton("Groups", hide=True), "Groups")
        self.add_tab(QLabel("PermissionGroups"), ProjectTabButton("PermissionGroups", hide=True), "PermissionGroups")
        self.add_tab(QLabel("Files"), ProjectTabButton("Files", hide=True), "Files")
        self.add_tab(QLabel("Tasks"), ProjectTabButton("Tasks", hide=True), "Tasks")
        self.add_tab(QLabel("Timelogs"), ProjectTabButton("Timelogs", hide=True), "Timelogs")
        self.add_tab(QLabel("Tags"), ProjectTabButton("Tags", hide=True), "Tags")
        self.add_tab(QLabel("Status"), ProjectTabButton("Status", hide=True), "Status")
        self.add_tab(QLabel("PipelineSteps"), ProjectTabButton("PipelineSteps", hide=True), "PipelineSteps")
        self.add_tab(QLabel("Playlists"), ProjectTabButton("Playlists", hide=True), "Playlists")

        projectMenu = OtherMenu(self)
        self.otherTabButton = ProjectTabButton("Others", menu=projectMenu)
        self.add_tab(QLabel("Others"), self.otherTabButton, "Others")

        # self.add_tail(QLabel("zzz"))

        self.load_tab()

        self.setObjectName("ProjectMainWindow")
        self.tabWidget.setObjectName("ProjectMainWindowTab")

        self.set_back_color("rgb(200,200,200)")
        styleText = resource.get_style("project")
        self.setStyleSheet(styleText)

    def set_core_property(self, **kwargs):
        super(ProjectMainWindow, self).set_core_property(**kwargs)
        if self.coreproperty_apply:
            logger.debug((self.__class__.__name__, kwargs))
            if 'showId' not in kwargs and 'showName' in kwargs:
                self.showId = Project.get(name=self.showName).id
            if 'showName' not in kwargs and 'showId' in kwargs:
                self.showName = Project.get(id=self.showId).name
            self.projectLabel.setText(self.showName)
            self.mediaWindow.set_core_property(showList=[self.showId, ])
            self.shotsWindow.set_core_property(showId=self.showId)

    def update_data(self):
        print "update_data, project: ", self.showName
        logger.debug((self.__class__.__name__, self.showName))


class OtherMenu(QMenu):
    chooseItem = Signal(list)
    def __init__(self, parent=None):
        super(OtherMenu, self).__init__(parent)

        for page in PROJECT_PAGES:
            action = QAction(resource.get_qicon("icon", page + ".png"), page, self)
            action.triggered.connect(self.action_triggered)
            self.addAction(action)

        styleText = resource.get_style("pagemenu")
        self.setStyleSheet(styleText)

    def action_triggered(self):
        pageList = [
            {"pagename": self.sender().text(), "coreproperty": {}}
        ]
        self.chooseItem.emit(pageList)
        self.parent().otherTabButton.set_selected(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = ProjectMainWindow()
    panel.set_core_property(**{"showId":1, "showName":"DRM"})
    # panel.surl = [{'pagename': 'Project', 'coreproperty': {'showName': 'DRM'}}]
    # panel.to_tab("Shots")
    # panel.apply_page_data('sins://page/Media')
    panel.apply_page_data('sins://page/Shots/Detail?showId=1&shotId=1')
    panel.show()
    app.exec_()