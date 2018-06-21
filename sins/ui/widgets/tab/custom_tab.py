# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 3/31/2018

import sys
from sins.module.sqt import *
from sins.utils.res import resource
from sins.utils.surl.surl import SURL
from sins.utils.color import get_lum, other_to_rgb
from sins.ui.utils import get_text_wh


class CustomTabButton(QLabel):
    chooseItem = Signal(list)

    def __init__(self,
                 text,
                 colorDict=None,
                 icon=None,
                 icon_size=25,
                 pulldown=None,
                 menu=None,
                 height=50,
                 marginSize=10,
                 hide=False,
                 parent=None):
        super(CustomTabButton, self).__init__(parent)

        self.labeltext = text
        self.colorDict = colorDict
        self.icon = icon
        self.icon_size = icon_size
        self.pulldown = pulldown
        self.menu = menu
        self.fixheight = height
        self.is_hiden = hide
        self.marginSize = marginSize

        self.index = 0
        self.coreproperty = {}
        self.defaultPage = []

        self.init_ui()

    def init_ui(self):

        self.pulldownSize = 20

        self.setFixedHeight(self.fixheight)
        self.setFont(QFont("Arial", 8))
        text = str(self.labeltext)
        text_width, text_height = get_text_wh(text, self.font())
        self.textPos = QPoint(self.marginSize, (self.height() - text_height) / 2.0)

        width = text_width
        width = text_width + self.marginSize * 2
        if text == "":
            text_width = 0
            width = 10
        if self.icon is not None:
            iconMargin = 2
            width = width + self.icon_size + iconMargin * 2
            self.iconPos = QPoint(self.marginSize + iconMargin, (self.height() - self.icon_size) / 2.0)
            self.textPos = self.textPos + QPoint(self.icon_size + iconMargin * 2, 0)
        if self.pulldown is not None or self.menu is not None:
            width = width + 10
            self.pulldownPos = QPoint(width - self.marginSize, (self.height() - self.pulldownSize) / 2.0)
        self.setFixedWidth(width + 10)
        self.textRect = QRect(self.textPos.x(), self.textPos.y(), text_width + 10, text_height)

        self.set_selected(False)
        self.set_style()

        if self.pulldown != None:
            self.combo = QComboBox(self)
            self.combo.setModel(self.pulldown.model())
            self.combo.setView(self.pulldown)
            self.combo.hide()
            self.combo.setFixedHeight(self.height())
            if hasattr(self.pulldown, 'chooseItem'):
                self.pulldown.chooseItem.connect(self.choose_pulldown_item)

        if self.menu is not None:
            self.toolButton = QToolButton(self)
            self.toolButton.setPopupMode(QToolButton.InstantPopup)
            self.toolButton.setMenu(self.menu)
            self.toolButton.setFixedHeight(self.height())
            self.toolButton.hide()
            if hasattr(self.menu, 'chooseItem'):
                self.menu.chooseItem.connect(self.choose_menu_item)

    def paintEvent(self, QPaintEvent):
        super(CustomTabButton, self).paintEvent(QPaintEvent)
        painter = QPainter(self)
        painter.setFont(self.font())
        if self.icon != None:
            if isinstance(self.icon, basestring):
                icon = resource.get_pixmap(self.icon, scale=self.icon_size)
            elif isinstance(self.icon, QPixmap):
                icon = self.icon.scaled(self.icon_size, self.icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(self.iconPos, icon)
        if self.labeltext != "":
            painter.drawText(self.textRect, Qt.AlignCenter, self.labeltext)
        if self.pulldown is not None or self.menu is not None:
            background = self.colorDict["background"]
            lum = get_lum(other_to_rgb(background))
            if lum < 0.5:
                pulldownicon = resource.get_pixmap("button", "arrow_down1_white.png", scale=self.pulldownSize)
            else:
                pulldownicon = resource.get_pixmap("button", "arrow_down1_darkgray.png", scale=self.pulldownSize)
            painter.drawPixmap(self.pulldownPos, pulldownicon)
        # super(CustomTabButton, self).paintEvent(QPaintEvent)

    def set_style(self):
        if self.colorDict:
            color = self.colorDict["color"]
            background = self.colorDict["background"]
            hovercolor = self.colorDict["hovercolor"]
            hoverbackground = self.colorDict["hoverbackground"]
            selectedcolor = self.colorDict["selectedcolor"]
            selectedbackground = self.colorDict["selectedbackground"]

            self.setStyleSheet("""
            CustomTabButton{
                color:%s;
                background:%s;
            }
            CustomTabButton[hover=true]{
                color:%s;
            }
            CustomTabButton:hover{
                background:%s;
            }
            CustomTabButton[selected=true]{
                color:%s;
                background:%s;
            }
            """ % (color, background, hovercolor, hoverbackground, selectedcolor, selectedbackground))

    def set_index(self, index):
        self.index = index

    def set_selected(self, selected):
        self.setProperty("selected", selected)
        self.set_style()

    def set_core_property(self, kwargs={}):
        self.coreproperty = kwargs

    def choose_pulldown_item(self, pageList):
        self.chooseItem.emit(pageList)
        self.combo.hidePopup()

    def choose_menu_item(self, pageList):
        self.chooseItem.emit(pageList)
        self.toolButton.menu().hide()

    def enterEvent(self, *args, **kwargs):
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("hover", True)
        self.set_style()

    def leaveEvent(self, *args, **kwargs):
        self.setCursor(Qt.ArrowCursor)
        self.setProperty("hover", False)
        self.set_style()

    def mousePressEvent(self, QMouseEvent):
        if self.pulldown is not None:
            self.combo.showPopup()
        if self.menu is not None:
            self.toolButton.showMenu()

    def mouseReleaseEvent(self, QMouseEvent):
        if self.pulldown is None and self.menu is None:
            pagelist = [{"pagename":self.labeltext, "coreproperty":self.coreproperty}]
            pagelist.extend(self.defaultPage)
            self.chooseItem.emit(pagelist)


class DefaultTabButton(CustomTabButton):
    def __init__(self, text, *args, **kwargs):
        colorDict = {
            "color":"black",
            'background':"gray",
            "hovercolor":"black",
            "hoverbackground":"gray",
            "selectedcolor":"black",
            "selectedbackground":"white"
        }
        super(DefaultTabButton, self).__init__(text, colorDict, height=35, *args, **kwargs)


class MainTabButton(CustomTabButton):
    def __init__(self, text, *args, **kwargs):
        colorDict = {
            "color":"white",
            'background':"rgb(30,30,30)",
            "hovercolor":"white",
            "hoverbackground":"rgb(45,45,45)",
            "selectedcolor":"white",
            "selectedbackground":"rgb(70,70,70)"
        }
        super(MainTabButton, self).__init__(text, colorDict, *args, **kwargs)


class ProjectTabButton(CustomTabButton):
    def __init__(self, text, *args, **kwargs):
        colorDict = {
            "color":"black",
            'background':"rgb(200, 200, 200)",
            "hovercolor":"black",
            "hoverbackground":"rgb(170, 170, 170)",
            "selectedcolor":"black",
            "selectedbackground":"rgb(150, 150, 150)"
        }
        super(ProjectTabButton, self).__init__(text, colorDict, height=35, *args, **kwargs)


class MediaTabButton(CustomTabButton):
    def __init__(self, text, *args, **kwargs):
        colorDict = {
            "color":"black",
            'background':"rgb(200, 200, 200)",
            "hovercolor":"black",
            "hoverbackground":"rgb(170, 170, 170)",
            "selectedcolor":"white",
            "selectedbackground":"rgb(40, 55, 60)"
        }
        super(MediaTabButton, self).__init__(text, colorDict, height=35, *args, **kwargs)


class CustomTabBar(QWidget):
    selectTab = Signal(int)
    def __init__(self):
        super(CustomTabBar, self).__init__()

        self.backLabel = QLabel(self)

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)

        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)

        self.headButton = None
        self.allTabButtons = []
        self.selectedTab = None
        self.tailButtons = []
        self.selectedIndex = 0


    def add_tab_button(self, widget=None):
        self.allTabButtons.append(widget)

    def add_head_button(self, widget=None):
        self.headButton = widget

    def add_tail_button(self, widget=None):
        self.tailButtons.append(widget)

    def load_tab_buttons(self):
        for index, button in enumerate(self.allTabButtons):
            button.set_index(index)
            self.layout.addWidget(button)
            if button.is_hiden:
                button.setVisible(False)

    def load_head_button(self):
        if self.headButton is not None:
            self.layout.addWidget(self.headButton)

    def load_tail_buttons(self):
        for i in self.tailButtons:
            self.layout.addWidget(i)

    def load_all_buttons(self, align):
        self.load_head_button()
        if align == Qt.AlignLeft:
            self.load_tab_buttons()
            self.layout.addStretch()
        elif align == Qt.AlignRight:
            self.layout.addStretch()
            self.load_tab_buttons()
        self.load_tail_buttons()

    def resizeEvent(self, QResizeEvent):
        super(CustomTabBar, self).resizeEvent(QResizeEvent)

        self.backLabel.resize(self.width(), self.height())


class CustomTabWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(CustomTabWindow, self).__init__(*args, **kwargs)

        self.customTabBar = CustomTabBar()
        self.tabWidget = QTabWidget()
        self.tabWidget.tabBar().hide()

        layout = QVBoxLayout()
        layout.addWidget(self.customTabBar)
        layout.addWidget(self.tabWidget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.widgetList = []


    def add_tab(self, widget, tabwidget, text):
        self.customTabBar.add_tab_button(tabwidget)
        setattr(widget, "labeltext", text)
        setattr(widget, "upperpage", self)
        self.widgetList.append(widget)
        self.tabWidget.addTab(widget, text)

    def add_head(self, widget):
        self.customTabBar.add_head_button(widget)

    def add_tail(self, widget):
        self.customTabBar.add_tail_button(widget)

    def load_tab(self, align=Qt.AlignLeft):
        self.customTabBar.load_all_buttons(align)
        self.create_tab_signal()

    def create_tab_signal(self):
        for i in self.customTabBar.allTabButtons:
            i.chooseItem.connect(self.apply_page_data)

    def apply_page_data(self, pageinfo):
        # print pageinfo
        pagelist = []
        if isinstance(pageinfo, list):
            pagelist = pageinfo
        else:  # str, QString
            pagelist = SURL(str(pageinfo)).convert_to_page()
        # print pagelist
        currentWidget = self
        for index, pageDict in enumerate(pagelist):
            if currentWidget is not None and isinstance(currentWidget, CustomTabWindow):
                # print currentWidget
                currentWidget = currentWidget.to_tab(pageDict["pagename"])
                # print currentWidget
                if hasattr(currentWidget, "set_core_property"):
                    if pageDict["coreproperty"] != {}:
                        currentWidget.set_core_property(**pageDict["coreproperty"])
                else:
                    print currentWidget, "model_attr 'set_core_property' not exist"

                if hasattr(currentWidget, "surl"):
                    # print [pageDict]
                    if hasattr(currentWidget, "upperpage") and hasattr(currentWidget.upperpage, "surl"):
                        upperpage = currentWidget.upperpage
                        # print 'upperpage.surl.url', upperpage, upperpage.surl.url, type(upperpage.surl.url)
                        # print 'SURL.page_to_url([pageDict])', [pageDict], SURL.page_to_url([pageDict])
                        upperURL = SURL(upperpage.surl.url)
                        currentWidget.surl = upperURL.append(SURL.page_to_url([pageDict], keep_query_keys=currentWidget.coreproperty_list))
                    else:
                        currentWidget.surl = [pageDict]
                else:
                    print currentWidget, "model_attr 'surl' not exist"

                if hasattr(currentWidget, "update_data"):
                    currentWidget.update_data()
                else:
                    print currentWidget, "model_attr 'update_data' not exist"

    def to_tab(self, name):
        # print 'to tab:', name
        for widgetObj in self.widgetList:
            if widgetObj.labeltext == name:
                index = self.tabWidget.indexOf(widgetObj)
                self.select_tab(index)
                return widgetObj

    def select_tab(self, index):
        # print 'select_tab', index
        for tabButton in self.customTabBar.allTabButtons:
            if tabButton.index == index:
                tabButton.set_selected(True)
                self.customTabBar.selectedTab = tabButton
                # print 'current tab:', self.customTabBar.selectedTab
            else:
                tabButton.set_selected(False)
        self.tabWidget.setCurrentIndex(index)

    def set_tab_background(self, color):
        self.tabBackground = color
        self.set_style()

    def set_back_color(self, color):
        self.customTabBar.backLabel.setStyleSheet("background:%s" % color)


class TestProjectTable(QTableWidget):
    chooseItem = Signal()
    def __init__(self):
        super(TestProjectTable, self).__init__()

        self.setRowCount(3)
        self.setColumnCount(2)

        data = {}
        data["ABCDE"] = {"age": 10, "height": 120, "weight": 40}
        data["CWT"] = {"age": 20, "height": 170, "weight": 60}

        for x, key in enumerate(data):
            # tableWidget.setItem(x, 0, QTableWidgetItem(key))
            item0 = QTableWidgetItem(key)
            item0.setTextAlignment(Qt.AlignCenter)
            self.setItem(x, 0, item0)
            self.setItem(x, 1, QTableWidgetItem(str(data[key]["age"])))

        self.resizeColumnsToContents()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)

        self.setStyleSheet("QAbstractItemView{min-width:200px;}")


class TestTabWindow(CustomTabWindow):
    def __init__(self):
        super(TestTabWindow, self).__init__()

        testList = QListWidget()
        testList.addItems(["aa", "bb", "cc"])

        self.add_tab(QLabel("Artist"), MainTabButton("Artist"), "Artist")
        self.add_tab(QLabel("Project"), MainTabButton("Project", pulldown=TestProjectTable()), "Project")
        self.add_tab(QLabel("Media"), MainTabButton("Media", icon=resource.get_pic("button/playButton_blue.png"), parent=self), "Media")
        self.add_head(MainTabButton("LOGO"))
        self.add_tail(QLineEdit())
        self.add_tail(MainTabButton("ZZZ"))
        self.load_tab()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestTabWindow()
    window.to_tab("Artist")
    window.show()
    sys.exit(app.exec_())

