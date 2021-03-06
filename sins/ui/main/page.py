# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/22/2018

import sys
from sins.module.sqt import *
from sins.ui.main.artist.artist import ArtistMainWindow
from sins.ui.main.project.project import ProjectMainWindow
from sins.ui.main.media.media import MediaMainWindow
from sins.ui.widgets.tab.custom_tab import CustomTabWindow, MainTabButton
from sins.ui.widgets.action import SeparatorAction
from sins.ui.widgets.label import RoundLabel, RoundRectLabel
from sins.db.models import *
from sins.db.current import current_user_object
from sins.db.permission import get_permission_projects


PageMenuStyle = resource.get_style("pagemenu")
PageStyle = resource.get_style("page")


class SignalLabel(QLabel):
    enter = Signal()
    press = Signal()
    release = Signal()
    leave = Signal()

    def __init__(self, *args, **kwargs):
        super(SignalLabel, self).__init__(*args, **kwargs)

    def enterEvent(self, event):
        self.enter.emit()

    def mousePressEvent(self, event):
        self.press.emit()

    def mouseReleaseEvent(self, event):
        self.release.emit()

    def leaveEvent(self, event):
        self.leave.emit()


class UserButton(QWidget):
    def __init__(self, *args, **kwargs):
        super(UserButton, self).__init__(*args, **kwargs)

        self.normalColor = 'transparent'
        self.hoverColor = 'rgb(45,45,45)'
        self.pressColor = 'rgb(70,70,70)'

        self.init_ui()
        self.create_menu()

    def init_ui(self):
        self.backLabel = QLabel(self)

        self.userThumbnail = RoundLabel()
        self.userThumbnail.setFixedSize(30, 30)
        thumbnail = current_user_object.thumbnail
        if thumbnail is not None and os.path.exists(thumbnail.host_path):
            self.userThumbnail.setPixmap(resource.get_pixmap(thumbnail.host_path))
        else:
            self.userThumbnail.setPixmap(resource.get_pixmap('icon', 'User1.png'))
        self.pulldownButton = QLabel()
        self.pulldownButton.setAlignment(Qt.AlignCenter)
        self.pulldownButton.setPixmap(resource.get_pixmap('button', 'arrow_down1_white.png', scale=20))
        self.pulldownButton.setFixedSize(20, 35)
        self.masterLayout = QHBoxLayout()
        self.masterLayout.addWidget(self.userThumbnail)
        # self.masterLayout.addSpacing(5)
        self.masterLayout.addWidget(self.pulldownButton)
        self.masterLayout.setAlignment(Qt.AlignLeft)
        self.masterLayout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(self.masterLayout)

        self.frontLabel = SignalLabel(self)
        self.frontLabel.enter.connect(self.after_enter)
        self.frontLabel.press.connect(self.after_press)
        self.frontLabel.release.connect(self.after_release)
        self.frontLabel.leave.connect(self.after_leave)

        # self.setFixedWidth(100)

        self.backLabel.setStyleSheet('background:%s;' % self.normalColor)

    def create_menu(self):
        self.toolButton = QToolButton(self)

        self.userMneu = QMenu(self)
        self.userMneu.setStyleSheet(PageMenuStyle)
        self.loginAction = SeparatorAction('Logged in as {}'.format(current_user), self)
        self.loginAction.setEnabled(False)
        self.aboutAction = QAction('About', self)
        self.profileAction = QAction('Profile', self)
        self.logoutAction = QAction('Log Out', self)

        self.userMneu.addAction(self.loginAction)
        self.userMneu.addSeparator()
        self.userMneu.addAction(self.aboutAction)
        self.userMneu.addAction(self.profileAction)
        self.userMneu.addAction(self.logoutAction)

        self.toolButton.setPopupMode(QToolButton.InstantPopup)
        self.toolButton.setMenu(self.userMneu)
        self.toolButton.setFixedHeight(50)
        self.toolButton.hide()

    def resizeEvent(self, *args, **kwargs):
        super(UserButton, self).resizeEvent(*args, **kwargs)
        self.backLabel.setFixedSize(self.size())
        self.frontLabel.setFixedSize(self.size())

    def after_enter(self):
        self.backLabel.setStyleSheet('background:%s;' % self.hoverColor)
        self.setCursor(Qt.PointingHandCursor)

    def after_press(self):
        self.backLabel.setStyleSheet('background:%s;' % self.pressColor)

    def after_release(self):
        self.toolButton.showMenu()
        self.backLabel.setStyleSheet('background:%s;' % self.hoverColor)

    def after_leave(self):
        self.backLabel.setStyleSheet('background:%s;' % self.normalColor)
        self.setCursor(Qt.ArrowCursor)


class PageWindow(CustomTabWindow):
    logoutclicked = Signal()

    def __init__(self, *args, **kwargs):
        super(PageWindow, self).__init__(*args, **kwargs)

        self.init_ui()

    def init_ui(self):

        self.logoLabel = QLabel("SINS")
        self.logoLabel.setObjectName("logoLabel")
        self.logoLabel.setFont(QFont("Roman times", 12, QFont.Bold))
        self.logoLabel.setFixedHeight(45)
        self.logoLabel.setMinimumWidth(70)
        self.logoLabel.setAlignment(Qt.AlignCenter)

        self.artistWindow = ArtistMainWindow()
        self.projectWindow = ProjectMainWindow(parent=self)
        # self.add_link_object(self.projectWindow)
        self.mediaWindow = MediaMainWindow()

        self.add_head(self.logoLabel)

        artistButton = MainTabButton("Artist")
        artistButton.defaultPage = [{"pagename":'My Task', "coreproperty":{}}]
        artistButton.set_core_property({'personId': current_user_object.id})
        self.add_tab(self.artistWindow, artistButton, "Artist")

        projectMenu = ProjectMenu()
        projectList = []
        projects = get_permission_projects(current_user_object)
        prefetch(projects, File)
        for project in projects:
            if project.thumbnail is not None:
                thumbnail_path = project.thumbnail.host_path
            else:
                thumbnail_path = resource.error_pic.Error02
            projectList.append({'name': project.code, 'id': project.id, 'thumb': thumbnail_path})
        projectMenu.refresh_list(projectList)
        self.add_tab(self.projectWindow, MainTabButton("Project", menu=projectMenu), "Project")

        mediaButton = MainTabButton("Media")
        mediaButton.set_core_property({'personId': current_user_object.id})
        self.add_tab(self.mediaWindow, mediaButton, "Media")

        self.userButton = UserButton()
        self.userButton.logoutAction.triggered.connect(self.log_out)
        self.add_tail(self.userButton)

        self.load_tab()

        self.setObjectName("PageWindow")
        self.tabWidget.tabBar().setObjectName("PageWindowTab_TabBar")
        self.tabWidget.setObjectName("PageWindowTab")

        self.set_back_color("rgb(30,30,30)")
        self.setStyleSheet(PageStyle)

    def log_out(self):
        self.logoutclicked.emit()


class ProjectListCellWidget(QWidget):
    mouseEnter = Signal(object)
    # mouseLeave = Signal()
    clicked = Signal()

    def __init__(self, projectDict={}, parent=None):
        super(ProjectListCellWidget, self).__init__(parent)

        self.projectName = projectDict["name"]
        self.projectId = projectDict["id"]

        self.backLabel = QLabel(self)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        # thumnLabel = QLabel()
        thumnLabel = RoundRectLabel(round=5)
        thumnLabel.setPixmap(resource.get_pixmap(projectDict["thumb"],
                                                 scale=[100, 56],
                                                 aspect='expand',
                                                 error='Error02'))
        thumnLabel.setFixedSize(100, 56)
        thumnLabel.setAlignment(Qt.AlignCenter)
        nameLabel = QLabel(projectDict["name"])
        arrowLabel = QLabel()
        arrowLabel.setPixmap(resource.get_pixmap("button", "arrow_right1_darkgray.png", scale=20))
        layout.addWidget(thumnLabel)
        layout.addSpacing(10)
        layout.addWidget(nameLabel)
        layout.addSpacing(20)
        layout.addWidget(arrowLabel)
        self.setLayout(layout)

        self.setMinimumWidth(200)

    def set_selected(self, value):
        if value:
            self.backLabel.setStyleSheet("background:rgb(190,190,190)")
        else:
            self.backLabel.setStyleSheet("background:transparent")

    def enterEvent(self, *args, **kwargs):
        super(ProjectListCellWidget, self).enterEvent(*args, **kwargs)
        self.mouse_enter()

    # def leaveEvent(self, *args, **kwargs):
    #     super(ProjectListCellWidget, self).leaveEvent(*args, **kwargs)
    #     self.mouseLeave.emit()

    def mouseReleaseEvent(self, *args, **kwargs):
        self.clicked.emit()

    def mouse_enter(self):
        # print "mouse_enter"
        self.globalPos = QCursor().pos() - self.mapFromGlobal(QCursor().pos())
        menuPos = self.globalPos + QPoint(self.width(), 0)
        # print self.globalPos, self.width(), self.height(), menuPos
        self.mouseEnter.emit(menuPos)

    def resizeEvent(self, QResizeEvent):
        super(ProjectListCellWidget, self).resizeEvent(QResizeEvent)
        self.backLabel.resize(self.size())


class PageMenu(QMenu):
    def __init__(self, parent=None):
        super(PageMenu, self).__init__(parent)
        self.setMouseTracking(True)
        self.rect2 = None

    def mouseMoveEvent(self, QMouseEvent):
        super(PageMenu, self).mouseMoveEvent(QMouseEvent)
        # print "PageMenu move", QMouseEvent.pos()
        # print "PageMenu move", QMouseEvent.globalPos()
        self.rect1 = self.geometry()
        # self.rect1.moveTo(0, 0)
        # print self.rect1, self.rect2
        pos = QMouseEvent.globalPos()
        if self.rect2 is not None:
            # print self.rect1.contains(pos), self.rect2.contains(pos)
            if not (self.rect1.contains(pos) or self.rect2.contains(pos)):
                self.close()
                self.rect2 = None


class ProjectMenu(QMenu):
    chooseItem = Signal(list)

    def __init__(self):
        super(ProjectMenu, self).__init__()

        self.selectedProjectName = None
        self.selectedProjectId = None

        self.setStyleSheet(PageMenuStyle)

        self.setMouseTracking(True)


    def refresh_list(self, projects=[]):
        self.allProjectWidgets = []
        self.addSeparator()
        recentAction = SeparatorAction("Recent", self)
        self.addAction(recentAction)
        for index, projectDict in enumerate(projects):
            projectAction = QWidgetAction(self)
            # projectAction = ProjectWidgetAction(projectDict, self)
            projectListCellWidget = ProjectListCellWidget(projectDict)
            setattr(projectListCellWidget, "action", projectAction)
            projectListCellWidget.mouseEnter.connect(self.show_page_menu)
            projectListCellWidget.clicked.connect(self.choose_item)
            projectAction.setDefaultWidget(projectListCellWidget)
            self.allProjectWidgets.append(projectListCellWidget)
            self.addAction(projectAction)

        self.create_page_menu()

        self.addSeparator()
        showAllAction = QAction("Show All", self)
        self.addAction(showAllAction)

    def create_page_menu(self):
        PROJECT_PAGES = ["Overview", "Assets", "Shots", "Tasks", "Versons", "Notes", "Media"]

        self.pagemenu = PageMenu(self)
        for page in PROJECT_PAGES:
            action = QAction(resource.get_qicon("icon", page + ".png"), page, self)
            action.triggered.connect(self.action_triggered)
            self.pagemenu.addAction(action)

        # actionGroup = QActionGroup(self)
        # actionGroup.addAction(QAction("aaa", self))
        # self.pagemenu.addActions(actionGroup)

    def show_page_menu(self, pos):
        # print "show_page_menu", self.sender().projectName
        self.select_project(self.sender())
        # print self.sender().geometry()
        self.selectedGeometry = self.sender().geometry()
        self.setActiveAction(self.sender().action)
        self.pagemenu.move(pos)
        self.pagemenu.rect2 = QRect(self.sender().globalPos.x(), self.sender().globalPos.y(),
                                    self.sender().width(), self.sender().height())

        self.pagemenu.show()

    def select_project(self, projectWidget):
        self.selectedProjectName = projectWidget.projectName if projectWidget is not None else None
        self.selectedProjectId = projectWidget.projectId if projectWidget is not None else None
        for i in self.allProjectWidgets:
            if i != projectWidget:
                i.set_selected(False)
            else:
                i.set_selected(True)

    def mouseMoveEvent(self, QMouseEvent):
        super(ProjectMenu, self).mouseMoveEvent(QMouseEvent)
        if self.activeAction() is not None:
            if self.activeAction().text() != '':
                self.select_project(None)

    def action_triggered(self):
        pageList = [
            {"pagename": "Project", "coreproperty": {"showName": self.selectedProjectName, "showId": self.selectedProjectId}},
            {"pagename": str(self.sender().text()), "coreproperty": {}},
            {"pagename": "All", "coreproperty": {}},
        ]
        self.chooseItem.emit(pageList)
        self.select_project(None)

    def choose_item(self):
        # print self.selectedProjectName
        if self.selectedProjectName is not None and self.selectedProjectId is not None:
            pageList = [
                {"pagename":"Project", "coreproperty":{"showName":self.selectedProjectName, "showId": self.selectedProjectId}},
                {"pagename": "Overview", "coreproperty": {}}
            ]
            self.chooseItem.emit(pageList)
            self.pagemenu.close()
            self.select_project(None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = PageWindow()
    # panel.to_tab("Artist")
    # panel.apply_page_data([{'pagename': 'Project', 'coreproperty': {'showName': 'DRM'}}, {'pagename': u'Overview', 'coreproperty': {}}])
    # panel.apply_page_data('shots://page/Project/Overview?showName=DRM')
    # panel.apply_page_data('sins://page/Project/Media?showName=DRM')
    panel.apply_page_data('sins://page/Project/Shots/Detail?showName=DRM')
    panel.show()
    app.exec_()