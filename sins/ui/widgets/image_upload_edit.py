# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/17/2018

import os
import sys
from sins.module.sqt import *
from sins.utils.res import resource
from sins.ui.widgets.file_dialog import FileDialog
from sins.test.test_res import TestPic


IMAGE_WIDTH = 400
IMAGE_HEIGHT = 300


class ImageUploadEdit(QWidget):
    applyClicked = Signal()

    def __init__(self, *args, **kwargs):
        super(ImageUploadEdit, self).__init__(*args, **kwargs)

        self.setWindowFlags(Qt.Dialog)
        self.setWindowTitle('Upload New Image')

        self.current_image = None

        self.init_ui()

        self.uploadButton.clicked.connect(self.upload_clicked)
        self.applyButton.clicked.connect(self.apply_clicked)
        self.cancelButton.clicked.connect(self.cancel_clicked)

    def init_ui(self):
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        self.uploadButton = QPushButton('Upload')
        self.applyButton = QPushButton('Apply')
        self.cancelButton = QPushButton('Cancel')
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.uploadButton)
        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(self.imageLabel)
        self.masterLayout.addLayout(self.buttonLayout)
        self.masterLayout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.masterLayout)

    def set_image(self, image_path):
        self.current_image = image_path
        self.imageLabel.setPixmap(resource.get_pixmap(image_path, scale=[IMAGE_WIDTH, IMAGE_HEIGHT]))

    def upload_clicked(self):
        panel = FileDialog()
        panel.set_filter('Image(*.jpg *.png)')
        result = panel.exec_()
        if result == FileDialog.Accepted:
            if len(panel.selectedFiles) > 0:
                self.set_image(panel.selectedFiles[0])
    
    def apply_clicked(self):
        self.applyClicked.emit()
        self.close()
    
    def cancel_clicked(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = ImageUploadEdit()
    panel.set_image(TestPic('user.png'))
    panel.show()
    app.exec_()





