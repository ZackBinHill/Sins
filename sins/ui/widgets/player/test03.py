# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/23/2018


from PyQt4.QtCore import *
from PyQt4.QtGui import *
Signal = pyqtSignal
import os
import sys
import time
import numpy
import cv2
import math

ThisFolder = os.path.dirname(__file__)
Icons_Folder = "%s/icons" % os.path.dirname(__file__)
Icon_Size = 24

if cv2.__version__.split(".")[0] == "2":
    cv2.CAPtureFromFile = cv2.cv.CaptureFromFile
    cv2.CAP_PROP_FPS = cv2.cv.CV_CAP_PROP_FPS
    cv2.CAP_PROP_FRAME_COUNT = cv2.cv.CV_CAP_PROP_FRAME_COUNT
    cv2.CAP_PROP_POS_FRAMES = cv2.cv.CV_CAP_PROP_POS_FRAMES
    cv2.CAP_PROP_FRAME_WIDTH = cv2.cv.CV_CAP_PROP_FRAME_WIDTH
    cv2.CAP_PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT




def get_frame_list(frameIn, frameOut):
    n = 4
    frameNum = frameOut - frameIn + 1
    framesEach = int(math.ceil(float(frameNum)/n))
    print "frame each %s" % framesEach
    frameStr = []
    for i in range(1, n):
        frameStr.append([(i-1)*framesEach+1, i*framesEach])
    frameStr.append([(n-1)*framesEach+1, frameOut])
    return frameStr




class Panel(QWidget):
    def __init__(self, parent=None):
        super(Panel, self).__init__(parent)

        self.playSlider = PlaySlider()
        layout = QVBoxLayout()
        layout.addWidget(self.playSlider)
        self.setLayout(layout)

        self.cap = None
        self.cacheFrames = {}
        self.cacheDone = False

        self.manualStart = 0

        # self.load_capture("test.mov")
        self.load_capture("test.mp4")
        # self.load_capture("%s/test2.mp4" % ThisFolder)
        # self.load_capture("%s/test1080.mov" % ThisFolder)
        # self.load_capture("%s/test3.mov" % ThisFolder)
        # self.cap = cv2.CAPtureFromFile('test.mp4')

        styleText = open("%s/style.css" % ThisFolder).read()
        self.setStyleSheet(styleText)

    def load_capture(self, capFile):
        self.cap = cv2.VideoCapture(capFile)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.frameNum = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameIn = 1
        self.frameOut = self.frameNum
        self.customFrameIn = 1
        self.customFrameOut = self.frameNum
        self.playSlider.setMinimum(1)
        self.playSlider.setMaximum(self.frameNum)
        self.playSlider.frameOut = self.frameNum
        self.capRatio = float(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) / self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.currentFrame = 1
        self.cache_cap(capFile)

    def cache_cap(self, capFile):
        frameList = get_frame_list(1, self.frameNum)
        print frameList
        self.cacheJobs = []
        for frameRange in frameList:
            cacheThread = CacheThread(capFile, frameRange[0], frameRange[1])
            cacheThread.cacheDone.connect(self.cache_done)
            cacheThread.cacheFrame.connect(self.cache_frame)
            self.cacheJobs.append(cacheThread)
        for cacheThread in self.cacheJobs:
            cacheThread.start()

    def cache_frame(self):
        print "cache_frame"
        self.cacheFrames.update(self.sender().cacheFrames)
        self.playSlider.set_cache(len(self.cacheFrames.keys()))
        print len(self.cacheFrames.keys())

    def cache_done(self):
        print "cache done"
        self.cacheDone = True
        self.cacheFrames.update(self.sender().cacheFrames)
        self.playSlider.set_cache(len(self.cacheFrames.keys()))
        self.cap.release()


class CacheThread(QThread):
    cacheDone = Signal()
    cacheFrame = Signal()
    def __init__(self, capFile, frameIn, frameOut):
        super(CacheThread, self).__init__()

        self.cap = cv2.VideoCapture(capFile)
        self.frameIn = frameIn
        self.frameOut = frameOut
        self.frameNum = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.cacheFrames = {}

    def run(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frameIn - 1)
        self.cacheFrames = {}
        for i in range(self.frameIn, self.frameOut + 1):
            ret, frame = self.cap.read()
            if ret:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                img_code = numpy.array(imgencode)
                imgdata = img_code.tostring()

                self.cacheFrames[i] = imgdata
                if i % 10 == 0:
                    self.cacheFrame.emit()

        self.cacheDone.emit()
        self.cap.release()


class PlaySlider(QSlider):
    changeFrameIn = Signal(int)
    changeFrameOut = Signal(int)
    def __init__(self):
        super(PlaySlider, self).__init__()

        self.setOrientation(Qt.Horizontal)
        self.percentIn = 0
        self.percentOut = 1
        self.showMark = False
        self.cacheValue = 0

        self.setFixedHeight(50)
        self.hover = False
        self.drawhover = False
        self.hoverValue = 3

        self.frameIn = 1
        self.dragFrameIn = False
        self.frameOut = 1
        self.dragFrameOut = False
        self.mousePressIn = False
        self.mousePressOut = False

        self.setMouseTracking(True)

    def paintEvent(self, QPaintEvent):
        super(PlaySlider, self).paintEvent(QPaintEvent)

        painter = QPainter(self)

        self.draw_mark(painter)
        self.draw_cache(painter)
        self.draw_hover(painter)

    def get_position(self, percent):
        return percent * self.width() + 5 - 10 * percent

    def get_percent(self, value):
        return float(value - 1) / (self.maximum() - 1)

    def draw_hover(self, painter):
        if self.hover and self.drawhover:
            pen = QPen(QColor(220, 220, 220))
            pen.setWidth(2)
            painter.setPen(pen)
            length = 10
            percent = self.get_percent(self.hoverValue)
            positionX = self.get_position(percent)
            y1 = (self.height() - length) / 2.0
            y2 = (self.height() - length) / 2.0 + length
            hoverline = QLine(QPoint(positionX, y1), QPoint(positionX, y2))
            painter.drawLine(hoverline)
            text = str(self.hoverValue)
            font = QFont("Arial", 10)
            fm = QFontMetrics(font)
            textWidth = fm.boundingRect(text).width()
            painter.setFont(font)
            textX = positionX - textWidth / 2.0
            if textX + textWidth > self.width():
                textX = self.width() - textWidth
            if textX < 0:
                textX = 0
            painter.drawText(textX, y1 - 5, text)

    def draw_mark(self, painter):
        if self.showMark:
            self.draw_mark_line(painter, "in")
            self.draw_mark_line(painter, "out")
            brush = QBrush(QColor(200, 200, 200, 50))
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            x1 = self.get_position(self.percentIn)
            x2 = self.get_position(self.percentOut)
            y1 = 0
            y2 = 20
            painter.drawRect(QRect(x1, y1, x2 - x1, y2))

    def draw_mark_line(self, painter, mark="in"):
        pen = QPen(QColor(200, 200, 200))
        pen.setWidth(3)
        painter.setPen(pen)
        if mark == "in":
            position = self.get_position(self.percentIn)
        if mark == "out":
            position = self.get_position(self.percentOut)
        painter.drawLine(QLine(QPoint(position, 0), QPoint(position, 15)))

        brush = QBrush(QColor(50, 50, 50, 0))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        y1 = 0
        y2 = 15
        frameLine = QLine(QPoint(position, y1), QPoint(position, y2))
        painter.drawLine(frameLine)
        rectWidth = 20
        if mark == "in":
            self.frameInRect = QRect(position - rectWidth / 2.0, 0, rectWidth, 20)
            painter.drawRect(self.frameInRect)
        if mark == "out":
            self.frameOutRect = QRect(position - rectWidth / 2.0, 0, rectWidth, 20)
            painter.drawRect(self.frameOutRect)

    def set_mark_in(self, value):
        self.frameIn = value
        self.percentIn = self.get_percent(value)
        # print self.percentIn
        self.update()

    def set_mark_out(self, value):
        self.frameOut = value
        self.percentOut = self.get_percent(value)
        self.update()

    def set_mark_visible(self, visible):
        self.showMark = visible
        self.update()

    def draw_cache(self, painter):
        pen = QPen(QColor(200, 200, 200, 200))
        pen.setWidth(1)
        painter.setPen(pen)
        cacheValue = self.cacheValue*self.width()
        painter.drawLine(QLine(QPoint(0, self.height()/2+5), QPoint(cacheValue, self.height()/2+5)))

    def set_cache(self, value):
        self.cacheValue = self.get_percent(value)
        self.update()

    def enterEvent(self, *args, **kwargs):
        self.hover = True

    def leaveEvent(self, *args, **kwargs):
        self.hover = False

    def mousePressEvent(self, QMouseEvent):
        if self.showMark:
            if self.frameInRect.contains(QMouseEvent.pos()) or self.frameOutRect.contains(QMouseEvent.pos()):
                if self.frameInRect.contains(QMouseEvent.pos()):
                    self.mousePressIn = True
                elif self.frameOutRect.contains(QMouseEvent.pos()):
                    self.mousePressOut = True
            else:
                super(PlaySlider, self).mousePressEvent(QMouseEvent)
                pos = QMouseEvent.pos().x() / float(self.width())
                self.setValue(pos * (self.maximum() - self.minimum()) + self.minimum())
        else:
            super(PlaySlider, self).mousePressEvent(QMouseEvent)
            pos = QMouseEvent.pos().x() / float(self.width())
            self.setValue(pos * (self.maximum() - self.minimum()) + self.minimum())

    def mouseReleaseEvent(self, QMouseEvent):
        super(PlaySlider, self).mouseReleaseEvent(QMouseEvent)
        self.mousePressIn = False
        self.dragFrameIn = False
        self.mousePressOut = False
        self.dragFrameOut = False
        self.setCursor(Qt.ArrowCursor)


    def mouseMoveEvent(self, QMouseEvent):
        super(PlaySlider, self).mouseMoveEvent(QMouseEvent)

        x = QMouseEvent.pos().x()
        precent = float(x) / self.width()
        self.hoverValue = int(round(self.minimum() + precent * (self.maximum() - self.minimum())))
        if self.hoverValue == self.value():
            self.drawhover = False
        else:
            self.drawhover = True

        if self.showMark:
            if self.frameInRect.contains(QMouseEvent.pos()) or self.frameOutRect.contains(QMouseEvent.pos()):
                self.setCursor(Qt.SizeHorCursor)
                if self.mousePressIn:
                    self.dragFrameIn = True
                    self.change_in()
                if self.mousePressOut:
                    self.dragFrameOut = True
                    self.change_out()
            else:
                if self.dragFrameIn:
                    self.change_in()
                elif self.dragFrameOut:
                    self.change_out()
                else:
                    self.setCursor(Qt.ArrowCursor)

        self.update()

    def change_in(self):
        if self.hoverValue <= self.frameOut:
            self.frameIn = self.hoverValue
            self.percentIn = self.get_percent(self.frameIn)
            self.changeFrameIn.emit(self.frameIn)

    def change_out(self):
        if self.hoverValue >= self.frameIn:
            self.frameOut = self.hoverValue
            self.percentOut = self.get_percent(self.frameOut)
            self.changeFrameOut.emit(self.frameOut)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = Panel()
    panel.show()
    app.exec_()
