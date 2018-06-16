# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/17/2018

import sys
import traceback
from sins.module.sqt import *
from sins.module.db import mysql, psycopg2
from sins.ui.widgets.labelbutton import QLabelButton


class FileButton(QLabelButton):
    def __init__(self, name):
        colorDict = {
            "normalcolor":"darkgray",
            "hovercolor":"darkgray",
            "clickcolor":"darkgray",
            "normalbackcolor":"transparent",
            "hoverbackcolor":"rgb(200,200,200)",
            "clickbackcolor":"darkgray"
        }
        super(FileButton, self).__init__(name, colorDict=colorDict, scale=24)


class InstallDialog(QDialog):
    def __init__(self):
        super(InstallDialog, self).__init__()

        self.init_ui()

        self.connectButton.clicked.connect(self.connect_to_db)
        self.cancelButton.clicked.connect(self.cancel_clicked)
        self.dataFileButton.buttonClicked.connect(self.choose_data_file_path)
        self.dataFileEdit.textChanged.connect(self.path_changed)

    def init_ui(self):

        self.setWindowTitle("Install")

        self.masterLayout = QVBoxLayout()

        self.installLabel = QLabel()
        self.installLabel.setFixedSize(QSize(400, 200))

        self.layout1 = QFormLayout()
        self.hostEdit = QLineEdit("localhost")
        self.portEdit = QLineEdit("5432")
        self.userEdit = QLineEdit("postgres")
        self.pwdEdit = QLineEdit('123456')
        self.pwdEdit.setEchoMode(QLineEdit.Password)
        self.layout1.addRow("Database Host: ", self.hostEdit)
        self.layout1.addRow("Database Port: ", self.portEdit)
        self.layout1.addRow("User: ", self.userEdit)
        self.layout1.addRow("Password: ", self.pwdEdit)

        self.layout2 = QHBoxLayout()
        self.layout2.setAlignment(Qt.AlignRight)
        self.connectButton = QPushButton("Connect")
        self.cancelButton = QPushButton("Cancel")
        self.layout2.addWidget(self.connectButton)
        self.layout2.addWidget(self.cancelButton)

        self.layout3 = QHBoxLayout()
        self.dataFileLabel = QLabel("Data Files Path: ")
        self.dataFileEdit = QLineEdit()
        self.dataFileButton = FileButton("icon/folder1")
        self.layout3.addWidget(self.dataFileLabel)
        self.layout3.addWidget(self.dataFileEdit)
        self.layout3.addWidget(self.dataFileButton)

        self.masterLayout.addWidget(self.installLabel)
        self.masterLayout.addLayout(self.layout1)
        self.masterLayout.addLayout(self.layout3)
        self.masterLayout.addLayout(self.layout2)

        self.setLayout(self.masterLayout)

        self.set_style()

    def connect_to_db(self):
        host = str(self.hostEdit.text())
        port = int(str(self.portEdit.text()))
        user = str(self.userEdit.text())
        password = str(self.pwdEdit.text())
        connect_dict = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
        }
        try:
            db = psycopg2.connect(**connect_dict)
            print "connect to database successful"
            db.close()
        except:
            print "connect to database failed, check host and password"
            traceback.print_exc()

    def cancel_clicked(self):
        self.close()

    def choose_data_file_path(self):
        path = QFileDialog.getExistingDirectory(self, "choose a folder to save file data", ".")
        self.dataFileEdit.setText(path)

    def path_changed(self):
        self.dataFileEdit.setProperty("valid", os.path.exists(str(self.dataFileEdit.text())))
        self.set_style()

    def set_style(self):
        self.setStyleSheet("""
        QLineEdit[valid=true]{
            background:transparent;
        }
        QLineEdit[valid=false]{
            background:red;
        }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = InstallDialog()
    panel.show()
    app.exec_()