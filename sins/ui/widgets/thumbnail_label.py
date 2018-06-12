# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/10/2018

import os
import sys
import sins.module.cv as cv2
from sins.module.sqt import *
from opencv import CacheThread, ReadThread, convert_img_from_frame, convert_img_from_string
from sins.test.test_res import TestMov
from sins.utils.res import resource
from sins.utils.const import VIDEO_EXT, IMG_EXT


MAX_CACHE_FRAMES = 50.0


class ThumbnailLabel(QWidget):
    cacheDone = Signal()
    def __init__(self, parent=None, dynamic=False, has_button=False, background='black'):
        super(ThumbnailLabel, self).__init__(parent)

        self.dynamic = dynamic

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.backLabel = QLabel(self)
        self.backLabel.setStyleSheet("background:{}".format(background))

        self.label = ViewLabel(parent=self)
        # self.label.setAlignment(Qt.AlignCenter)
        self.label.setText("Loading...")
        self.label.hasButton = has_button
        self.label.setScaledContents(True)

        self.cap = None
        self.cacheFrames = {}
        self.capRatio = 0  # 16.0/9
        self.currentF = 0
        self.targetHeight = 0

        self.create_connect()

    def create_connect(self):
        if self.dynamic:
            self.label.mouseMove.connect(self.set_frame)
            self.label.mouseLeave.connect(self.default_frame)

    def create_preview(self, previewFile=None):
        self.versonPreviewFile = previewFile
        if self.versonPreviewFile == None:
            self.label.setText("No preview image")
        elif not os.path.exists(self.versonPreviewFile):
            self.label.setText("Loading...")
        else:
            if os.path.splitext(previewFile)[1] in IMG_EXT:
                self.load_picture(previewFile)
                self.label.hasButton = False
            elif os.path.splitext(previewFile)[1] in VIDEO_EXT:
                self.load_capture(previewFile)
            else:
                self.label.setText("No preview image")


    def load_picture(self, imgFile):
        self.read_file(imgFile)

    def load_capture(self, capFile):
        # print capFile
        self.capfile = capFile
        self.cap = cv2.VideoCapture(capFile)
        self.frameNum = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.capRatio = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if self.dynamic:
            self.cache_cap(capFile)
        else:
            self.read_file(capFile)

    def read_file(self, readFile):
        if self.cap is not None:
            self.readThread = ReadThread(readFile, cap=self.cap, frame=min(self.frameNum / 2, 20))
        else:
            self.readThread = ReadThread(readFile, fixwidth=200)
        self.readThread.readDone.connect(self.read_done)
        self.readThread.start()

    def read_done(self, img):
        # print "read done"
        shape = img.shape
        self.capRatio = float(shape[1]) / shape[0]
        pixmap = convert_img_from_frame(img)
        self.label.setPixmap(pixmap)
        self.set_resize_size()
        self.cacheDone.emit()

    def cache_cap(self, capFile):
        self.step = 1
        if self.frameNum > MAX_CACHE_FRAMES:
            self.step = int(self.frameNum / MAX_CACHE_FRAMES)
        # print step
        self.cacheThread = CacheThread(capFile,
                                       cap=self.cap,
                                       frameIn=1,
                                       frameOut=self.frameNum,
                                       step=self.step,
                                       fixwidth=200,
                                       readfile=True,
                                       tofile=True)
        # self.cacheThread = CacheThread(capFile, 1, self.frameNum, step=self.step, fixwidth=200, readfile=True, tofile=True)
        self.cacheThread.cacheDone.connect(self.cache_done)
        self.cacheThread.start()

    def cache_done(self):
        self.cacheFrames.update(self.cacheThread.cacheFrames)
        print "cache done"
        # print len(self.cacheFrames.keys()), self.cacheFrames.keys()
        self.cap.release()
        self.default_frame()
        self.set_resize_size()

    def default_frame(self):
        if self.dynamic:
            self.set_frame(0.5)

    def set_frame(self, percent):
        # print 'set_frame', percent
        if hasattr(self, "frameNum"):
            i = int(percent * self.frameNum)
            # print percent, i
            for j in range(i, i + self.step):
                if j in self.cacheFrames:
                    if j != self.currentF:
                        self.label.setPixmap(self.get_cache_frame(j))
                        self.currentF = j
                        break

    def get_cache_frame(self, i):
        cachefile = os.path.abspath(self.capfile) + ".%s" % i
        if os.path.exists(cachefile):
            return self.convert_img_from_file(cachefile)
        else:
            return self.convert_img_from_string(self.cacheFrames[i])

    def convert_img_from_file(self, cachefile):
        f = open(cachefile, "rb")
        data = f.read()
        f.close()
        return self.convert_img_from_string(data)

    def convert_img_from_string(self, imgdata):
        return convert_img_from_string(imgdata)

    def resizeEvent(self, QResizeEvent):
        # self.set_resize_size()
        super(ThumbnailLabel, self).resizeEvent(QResizeEvent)
        self.set_resize_size()

    def set_resize_size(self):
        currentW = self.width()
        currentH = self.height()
        # print 'current:', currentW, currentH
        if self.capRatio > 0:
            self.targetHeight = currentW / self.capRatio
            if currentH > 0:
                if currentW / float(currentH) > self.capRatio:
                    h = currentH
                    w = h * self.capRatio
                else:
                    w = currentW
                    h = w / self.capRatio
                self.label.resize(w, h)
                self.label.move((currentW - w) / 2, (currentH - h) / 2)
        else:
            self.label.move((currentW - self.label.width()) / 2, (currentH - self.label.height()) / 2)
        self.backLabel.setFixedSize(self.size())
        # print self.label.size(), self.capRatio



class ViewLabel(QLabel):
    labelclicked = Signal()
    mouseMove = Signal(float)
    mouseLeave = Signal()
    def __init__(self, parent=None):
        super(ViewLabel, self).__init__(parent)
        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignCenter)

        self.hasButton = True

        self.status = 0
        self.borderRect = QRect(0, 0, 0, 0)

        self.setStyleSheet("color:white")

    def paintEvent(self, QPaintEvent):
        super(ViewLabel, self).paintEvent(QPaintEvent)

        if self.hasButton:
            painter = QPainter(self)
            if self.status != 0:
                self.draw_button_border(painter)
            if self.status == 2:
                self.draw_back(painter)
                self.draw_button(painter)

    def draw_button_border(self, painter):
        point1 = [(self.width() - 50) / 2, (self.height() - 50) / 2]
        point2 = [50, 50]
        brush = QBrush(QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        self.borderRect = QRect(point1[0], point1[1], point2[0], point2[1])
        painter.drawRect(self.borderRect)

    def draw_back(self, painter):
        brush = QBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawRect(rect)

    def draw_button(self, painter):
        point1 = [(self.width()-50)/2, (self.height()-50)/2]
        image = resource.get_pixmap("button", "playButton_blue.png", scale=50)
        painter.drawPixmap(QPoint(point1[0], point1[1]), image)

    def enterEvent(self, event):
        super(ViewLabel, self).enterEvent(event)
        self.status = 1
        self.update()

    def mouseMoveEvent(self, event):
        super(ViewLabel, self).mouseMoveEvent(event)
        if self.hasButton:
            self.pos = event.pos()
            if self.borderRect.contains(self.pos):
                self.status = 2
                self.setCursor(Qt.PointingHandCursor)
            else:
                self.status = 1
                self.setCursor(Qt.ArrowCursor)
            self.update()

        x = event.pos().x()
        self.mouseMove.emit(float(x) / self.width())

    def mouseReleaseEvent(self, QMouseEvent):
        self.labelclicked.emit()

    def leaveEvent(self, *args, **kwargs):
        self.status = 0
        self.update()
        self.mouseLeave.emit()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # panel = DataWidget()
    panel = ThumbnailLabel(dynamic=True)
    # panel.create_preview(TestMov("test.jpg"))
    # panel.create_preview(TestMov("test3.mov"))
    panel.create_preview(TestMov("test.mp4"))
    panel.show()
    app.exec_()
