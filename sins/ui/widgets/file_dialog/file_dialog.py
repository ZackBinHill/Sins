# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/6/2018

from sins.module.sqt import *
from sins.ui.widgets.labelbutton import QLabelButton
from sins.utils.path.file import get_detail_of_path, get_dirs, get_files
from sins.utils.path.sequence import get_sequences
from sins.utils.res import resource
import sys
import os
import re


class ArrowButton(QLabelButton):
    def __init__(self, name):
        colorDict = {
            "normalcolor":"darkgray",
            "hovercolor":"darkgray",
            "clickcolor":"darkgray",
            "normalbackcolor":"transparent",
            "hoverbackcolor":"rgb(200,200,200)",
            "clickbackcolor":"darkgray"
        }
        super(ArrowButton, self).__init__(name, colorDict=colorDict, scale=24)


class FavoriteListItem(QListWidgetItem):
    def __init__(self, text, path, parent=None):
        super(FavoriteListItem, self).__init__(text, parent)
        self.path = path


class FileTreeItem(QTreeWidgetItem):
    def __init__(self, detailDict, parent=None):
        super(FileTreeItem, self).__init__(parent)

        self.setText(0, detailDict["name"])
        self.setText(1, detailDict["type"])
        self.setText(2, detailDict["size"])
        self.setText(3, detailDict["modified date"])

        self.filePath = detailDict["file path"]
        self.name = detailDict["name"]

        if "frame range" in detailDict.keys() and detailDict["frame range"] is not None:
            self.setText(0, detailDict["name"] + " " + detailDict["frame range"])
            self.setText(1, detailDict["type"] + " sequence")

        if detailDict["type"] == "folder":
            self.setIcon(0, resource.get_qicon("icon", "folder1_darkgray.png"))


class FileDialog(QDialog):
    Accepted = 1
    Rejected = 0
    def __init__(self, currentPath=QDir.currentPath(), filter="All Files(*.*)", parent=None):
        super(FileDialog, self).__init__(parent)

        self.setWindowTitle("Open File")

        self.historyList = []
        self.favoritePath = []
        self.selectedFiles = None

        self.init_ui()
        self.set_signal()

        self.set_current_path(currentPath)
        self.load_default_favorite_path()
        self.set_filter(filter)

    def init_ui(self):

        self.masterLayout = QVBoxLayout()

        self.pathLayout = QHBoxLayout()
        self.filePathEdit = QLineEdit()
        self.upArrow = ArrowButton("arrow_up2")
        self.backwardArrow = ArrowButton("arrow_left2")
        self.forwardArrow = ArrowButton("arrow_right2")
        self.pathLayout.addWidget(self.filePathEdit)
        # self.pathLayout.addWidget(self.backwardArrow)
        # self.pathLayout.addWidget(self.forwardArrow)
        self.pathLayout.addWidget(self.upArrow)

        self.treeLayout = QHBoxLayout()
        self.treeLayout1 = QVBoxLayout()
        self.favoriteList = QListWidget()
        self.systemTree = QTreeView()
        self.fileSystemModel = QFileSystemModel(self.systemTree)
        self.fileSystemModel.setRootPath("/")
        self.fileSystemModel.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        self.systemTree.setModel(self.fileSystemModel)
        self.systemTree.setColumnWidth(0, 200)
        self.systemTree.setColumnHidden(1, True)
        self.systemTree.setColumnHidden(2, True)
        self.systemTree.setColumnHidden(3, True)
        self.treeLayout1.addWidget(self.favoriteList, 1)
        self.treeLayout1.addWidget(self.systemTree, 2)
        self.fileTree = QTreeWidget()
        self.fileTree.setHeaderLabels(["name", "type", "size", "modified date"])
        self.fileTree.setColumnWidth(0, 300)
        self.fileTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.fileTree.setSortingEnabled(True)
        # self.fileTree.setRootIsDecorated(False)
        self.treeLayout.addLayout(self.treeLayout1, 1)
        self.treeLayout.addWidget(self.fileTree, 3)

        self.selectedLayout = QHBoxLayout()
        self.selectedLayout.setAlignment(Qt.AlignRight)
        self.sequenceCheck = QCheckBox("Sequence")
        self.nameLabel = QLabel("File name")
        self.selectedFileEdit = QLineEdit()
        self.filterCombo = QComboBox()
        self.filterCombo.setMinimumWidth(150)
        self.selectedLayout.addWidget(self.sequenceCheck)
        self.selectedLayout.addSpacing(50)
        self.selectedLayout.addWidget(self.nameLabel)
        self.selectedLayout.addWidget(self.selectedFileEdit)
        self.selectedLayout.addWidget(self.filterCombo)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignRight)
        self.openButton = QPushButton("Open")
        self.cancelButton = QPushButton("Cancel")
        self.buttonLayout.addWidget(self.openButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.masterLayout.addLayout(self.pathLayout)
        self.masterLayout.addLayout(self.treeLayout)
        self.masterLayout.addLayout(self.selectedLayout)
        # self.masterLayout.addLayout(self.buttonLayout)
        self.masterLayout.addWidget(self.buttonBox)
        self.setLayout(self.masterLayout)

        self.resize(900, 500)

    def set_signal(self):
        self.systemTree.clicked.connect(self.system_tree_selected_changed)
        self.favoriteList.currentItemChanged.connect(self.favorite_list_selected_changed)
        self.upArrow.buttonClicked.connect(self.uparrow_clicked)
        self.filePathEdit.textChanged.connect(self.path_changed)
        self.sequenceCheck.clicked.connect(self.refresh_file_tree)
        self.filterCombo.currentIndexChanged.connect(self.refresh_file_tree)
        self.fileTree.itemSelectionChanged.connect(self.file_selected_changed)
        self.fileTree.itemDoubleClicked.connect(self.file_double_clicked)
        self.openButton.clicked.connect(self.open_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)

    def load_default_favorite_path(self):
        self.add_favorite_path("home", QDir.homePath())
        self.add_favorite_path("%tmp%", QDir.tempPath())
        # for drive in QDir.drives():
        #     self.add_favorite_path(drive.filePath(), drive.filePath())

    def add_favorite_path(self, text, path):
        favoriteItem = FavoriteListItem(text, path)
        self.favoriteList.addItem(favoriteItem)

    def set_filter(self, filter):
        allFilter = filter.split(";;")
        self.filterCombo.addItems(allFilter)

    def set_current_path(self, path):
        # print path
        self.filePathEdit.setText(path)

    def system_tree_selected_changed(self, index):
        currentPath = self.fileSystemModel.filePath(index)
        self.set_current_path(currentPath)

    def favorite_list_selected_changed(self, item):
        currentPath = item.path
        self.set_current_path(currentPath)

    def uparrow_clicked(self):
        currentPath = str(self.filePathEdit.text())
        self.filePathEdit.setText(os.path.dirname(currentPath))

    def path_changed(self, path):
        if os.path.isdir(path):
            self.refresh_file_tree()

    def refresh_file_tree(self):
        show_seq = self.sequenceCheck.isChecked()
        currentFilter = self.filterCombo.currentText()
        match = re.search(r'\((?P<each_filter>.*)\)', currentFilter)
        if match:
            filters = match.group("each_filter")
            extList = []
            for ext in filters.split(" "):
                extList.append(ext[2:])
            # print extList
            currentPath = str(self.filePathEdit.text())
            self.fileTree.clear()
            allFiles = []
            for i in get_dirs(currentPath):
                allFiles.append(get_detail_of_path(i))
            allFileDetail = []
            if not show_seq:
                for i in get_files(currentPath):
                    allFileDetail.append(get_detail_of_path(i))
            else:
                for i in get_sequences(currentPath):
                    allFileDetail.append(get_detail_of_path(i))

            for detail in allFileDetail:
                if "*" in extList:
                    allFiles.append(detail)
                else:
                    if detail["type"].split(" ")[0] in extList:
                        allFiles.append(detail)

            for detail in allFiles:
                fileItem = FileTreeItem(detail)
                self.fileTree.addTopLevelItem(fileItem)
                # QCoreApplication.processEvents()

    def file_selected_changed(self):
        selectedNames = []
        self.selectedFiles = []
        for i in self.fileTree.selectedItems():
            selectedNames.append(i.name)
            self.selectedFiles.append(i.filePath)
        self.selectedFileEdit.setText(" ".join(selectedNames))

    def file_double_clicked(self, item):
        filePath = item.filePath
        if os.path.isdir(filePath):
            self.filePathEdit.setText(filePath)

    def open_clicked(self):
        self.close()

    def cancel_clicked(self):
        self.selectedFiles = None
        self.close()

    # def accept(self):
    #     super(FileDialog, self).accept()
    #
    # def reject(self):
    #     super(FileDialog, self).reject()


class TestWidget(QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()

        self.button = QPushButton("aaa", self)
        self.button.clicked.connect(self.show_dialog)

    def show_dialog(self):
        panel = FileDialog()
        result = panel.exec_()
        if result == FileDialog.Accepted:
            print panel.selectedFiles


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # panel = FileDialog()
    panel = TestWidget()
    panel.show()
    app.exec_()
