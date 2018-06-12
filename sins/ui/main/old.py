# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/10/2018

class ProjectListCellWidget(QWidget):
    mouseEnter = Signal(object)
    mouseLeave = Signal()
    clicked = Signal()
    def __init__(self, projectDict={}, parent=None):
        super(ProjectListCellWidget, self).__init__(parent)

        self.projectName = projectDict["name"]

        self.backLabel = QLabel(self)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        thumnLabel = QLabel()
        thumnLabel.setPixmap(QPixmap(projectDict["thumb"]).scaled(100, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        nameLabel = QLabel(projectDict["name"])
        arrowLabel = QLabel()
        arrowLabel.setPixmap(resource.get_pixmap("button", "arrow_right1_darkgray.png", scale=20))
        layout.addWidget(thumnLabel)
        layout.addWidget(nameLabel)
        layout.addWidget(arrowLabel)
        self.setLayout(layout)

        self.create_context_menu()

    def create_context_menu(self):
        PROJECT_PAGES = ["Overview", "Assets", "Shots", "Versons", "Notes", "Media"]

        self.menu = QMenu(self)
        # self.menu = PageMenu(self)
        for page in PROJECT_PAGES:
            action = QAction(resource.get_qicon("icon", page + ".png"), page, self)
            # action.triggered.connect(self.action_triggered)
            self.menu.addAction(action)
        # self.menu = QLabel("aaa")

    def close_context_menu(self):
        if not self.menu.geometry().contains(QCursor().pos()):
            self.menu.close()

    def show_context_menu(self, pos):
        # self.selectedProjectName = self.sender().projectName
        self.menu.move(pos)
        self.menu.show()
        # self.menu.exec_()

    def enterEvent(self, *args, **kwargs):
        super(ProjectListCellWidget, self).enterEvent(*args, **kwargs)
        self.backLabel.setStyleSheet("background:rgb(190,190,190)")
        self.mouse_enter()


    def leaveEvent(self, *args, **kwargs):
        super(ProjectListCellWidget, self).leaveEvent(*args, **kwargs)
        self.backLabel.setStyleSheet("background:transparent")
        self.mouseLeave.emit()


    def mouseReleaseEvent(self, *args, **kwargs):
        self.clicked.emit()

    def mouse_enter(self):
        # print "mouse_enter"
        self.globalPos = QCursor().pos() - self.mapFromGlobal(QCursor().pos())
        menuPos = self.globalPos + QPoint(self.width(), 0)
        # print self.globalPos, self.width(), self.height()
        self.mouseEnter.emit(menuPos)
        self.show_context_menu(menuPos)

    def resizeEvent(self, QResizeEvent):
        super(ProjectListCellWidget, self).resizeEvent(QResizeEvent)
        self.backLabel.resize(self.size())


class PageMenu(QMenu):
    def __init__(self, parent=None):
        super(PageMenu, self).__init__(parent)

    def leaveEvent(self, QEvent):
        super(PageMenu, self).leaveEvent(QEvent)
        print "leave"
        self.close()


class ProjectPullDown(QListWidget):
    chooseItem = Signal(list)
    def __init__(self):
        super(ProjectPullDown, self).__init__()

        self.selectedProject = None

        self.set_style()

    def set_style(self):
        self.setStyleSheet("""
        *{
            outline:0px
        }
        QAbstractItemView::item{
            height:70px;
        }
        QAbstractItemView{
            min-width:200px
        }
        QListView::item{
            color:black;
            background:white
        }
        QListView::item:hover{
            background:rgb(190,190,190)
        }
        QMenu{
            background:white;
            border:1px solid rgb(150,150,150)
        }
        QMenu::item{
            padding:5px 20px 5px 30px;
        }
        QMenu::item:selected{
            background:rgb(190,190,190)
        }
        """)

    def refresh_list(self, projects=[]):
        for index, projectDict in enumerate(projects):
            projectItem = QListWidgetItem(self)
            projectListCellWidget = ProjectListCellWidget(projectDict, parent=self)
            # projectListCellWidget.mouseEnter.connect(self.show_context_menu)
            # projectListCellWidget.mouseLeave.connect(self.close_context_menu)
            # projectListCellWidget.clicked.connect(self.choose_item)
            self.addItem(projectItem)
            self.setItemWidget(projectItem, projectListCellWidget)
            # self.setItemWidget(projectItem, QLabel("aaa"))
        # self.create_context_menu()
        # self.addItem("all")

    def create_context_menu(self):
        PROJECT_PAGES = ["Overview", "Assets", "Shots", "Versons", "Notes", "Media"]

        self.menu = QMenu(self)
        # self.menu = PageMenu(self)
        for page in PROJECT_PAGES:
            action = QAction(resource.get_qicon("icon", page + ".png"), page, self)
            action.triggered.connect(self.action_triggered)
            self.menu.addAction(action)
        # self.menu = QLabel("aaa")

    def close_context_menu(self):
        if not self.menu.geometry().contains(QCursor().pos()):
            self.menu.close()

    def show_context_menu(self, pos):
        self.selectedProject = self.sender().projectName
        self.menu.move(pos)
        self.menu.show()
        # self.menu.exec_()

    def action_triggered(self):
        pageList = [
            {"pagename": "Project", "coreproperty": {"showName": self.selectedProject}},
            {"pagename": self.sender().text(), "coreproperty": {}}
        ]
        self.chooseItem.emit(pageList)

    def choose_item(self):
        # print self.selectedProjectName
        pageList = [
            {"pagename":"Project", "coreproperty":{"showName":self.selectedProject}},
            {"pagename": "Overview", "coreproperty": {}}
        ]
        self.chooseItem.emit(pageList)
