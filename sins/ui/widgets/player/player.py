# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/23/2018

import sys
import time
import math
import sins.module.cv as cv2
from sins.module.sqt import *
from sins.utils.io.opencv import CacheThread, convert_img_from_frame, convert_img_from_string
from sins.test.test_res import TestMov
from sins.utils.res import resource

ThisFolder = os.path.dirname(__file__)
Icon_Size = 24

MAX_REFRESH_FPS = 100
CACHE_SEGMENTS = 4


def get_frame_list(frameIn, frameOut):
    n = CACHE_SEGMENTS
    frameNum = frameOut - frameIn + 1
    framesEach = int(math.ceil(float(frameNum)/n))
    # print "frame each %s" % framesEach
    frameStr = []
    for i in range(1, n):
        frameStr.append([(i-1)*framesEach+1, i*framesEach])
    frameStr.append([(n-1)*framesEach+1, frameOut])
    return frameStr


class Panel(QWidget):
    def __init__(self, parent=None):
        super(Panel, self).__init__(parent)

        self.initUi()

        self.cap = None
        self.cacheFrames = {}
        self.cacheDone = False
        self.fps = 1
        self.frameNum = 0
        self.frameIn = 1
        self.frameOut = 1
        self.customFrameIn = 1
        self.customFrameOut = 1
        self.lockRange = 0
        self.currentFrame = 1
        self.playThread = PlayThread()
        self.playThread.refresh.connect(self.next_frame)
        self.playThread.start()

        self.set_signal()

        self.manualStart = 0

        # self.load_capture(TestMov("test.mov"))
        # self.load_capture(TestMov("test.mp4"))
        # self.load_capture(TestMov("test2.mp4"))
        # self.load_capture(TestMov("test1080.mov"))
        # self.load_capture(TestMov("test3.mov"))
        self.load_capture(TestMov("out.mov"))

    def initUi(self):
        self.masterLayout = QVBoxLayout()
        self.label = QLabel()

        self.capTitleLayout = QHBoxLayout()
        self.capTitle = QLabel("test_v001")
        self.capTitleLayout.addWidget(self.capTitle)

        self.viewWidget = QWidget()
        self.viewWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.viewLabel = QLabel(self.viewWidget)
        self.viewLabel.setScaledContents(True)
        self.viewLabel.setStyleSheet("background:black")
        # self.viewLabel.setAutoFillBackground(True)
        self.viewLabel.setAlignment(Qt.AlignCenter)
        # self.viewLabel.setPixmap(QPixmap("test01.png"))

        self.sliderLayout = QHBoxLayout()
        self.frameInEdit = LineEdit("1")
        self.frameInEdit.setMaximumWidth(50)
        self.playSlider = PlaySlider()
        self.frameOutEdit = LineEdit("100")
        self.frameOutEdit.setMaximumWidth(50)
        self.sliderLayout.addWidget(self.frameInEdit)
        self.sliderLayout.addWidget(self.playSlider)
        self.sliderLayout.addWidget(self.frameOutEdit)

        self.buttonLayout = QHBoxLayout()
        self.fpsEdit = FpsLineEdit()
        self.fpsEdit.setMaximumWidth(50)
        self.frameInButton = LabelButton1(text="I")
        self.frameOutButton = LabelButton1(text="O")
        self.stopBackwardButton = LabelButton1(icon="stop")
        self.stopBackwardButton.setVisible(False)
        self.playBackwardButton = LabelButton1(icon="play_backward")
        self.stopForwardButton = LabelButton1(icon="stop")
        self.stopForwardButton.setVisible(False)
        self.playForwardButton = LabelButton1(icon="play_forward")
        self.lastFrameButton = LabelButton1(icon="last_frame")
        self.nextFrameButton = LabelButton1(icon="next_frame")
        self.skipBackwardButton = LabelButton1(icon="skip_backward")
        self.skipForwardButton = LabelButton1(icon="skip_forward")
        self.currentFrameEdit = LineEdit()
        self.currentFrameEdit.setMaximumWidth(50)
        self.skipStepsEdit = LineEdit("10")
        self.skipStepsEdit.setMaximumWidth(50)
        self.lockRangeButton = LabelButton2(icon="lock_range")

        self.buttonLayout.addWidget(self.fpsEdit)
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.frameInButton)
        self.buttonLayout.addWidget(self.lastFrameButton)
        self.buttonLayout.addWidget(self.stopBackwardButton)
        self.buttonLayout.addWidget(self.playBackwardButton)
        self.buttonLayout.addWidget(self.currentFrameEdit)
        self.buttonLayout.addWidget(self.stopForwardButton)
        self.buttonLayout.addWidget(self.playForwardButton)
        self.buttonLayout.addWidget(self.nextFrameButton)
        self.buttonLayout.addWidget(self.frameOutButton)
        self.buttonLayout.addSpacing(50)
        self.buttonLayout.addWidget(self.skipBackwardButton)
        self.buttonLayout.addWidget(self.skipStepsEdit)
        self.buttonLayout.addWidget(self.skipForwardButton)
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.lockRangeButton)

        self.masterLayout.addLayout(self.capTitleLayout)
        self.masterLayout.addWidget(self.viewWidget)
        self.masterLayout.addLayout(self.sliderLayout)
        self.masterLayout.addLayout(self.buttonLayout)
        self.setLayout(self.masterLayout)

        styleText = resource.get_style("player")
        self.setStyleSheet(styleText)

    def set_signal(self):
        self.fpsEdit.fpsChanged.connect(self.change_fps)
        self.playSlider.valueChanged.connect(self.manual_frame)
        self.playSlider.changeFrameIn.connect(self.change_frame_in)
        self.playSlider.changeFrameOut.connect(self.change_frame_out)
        self.playForwardButton.buttonClicked.connect(self.play_forward)
        self.stopForwardButton.buttonClicked.connect(self.stop_forward)
        self.playBackwardButton.buttonClicked.connect(self.play_backward)
        self.stopBackwardButton.buttonClicked.connect(self.stop_backward)
        self.nextFrameButton.buttonClicked.connect(self.next_frame)
        self.lastFrameButton.buttonClicked.connect(self.last_frame)
        self.skipBackwardButton.buttonClicked.connect(self.skip_backward)
        self.skipForwardButton.buttonClicked.connect(self.skip_forward)
        self.currentFrameEdit.editingFinished.connect(self.frame_edit_changed)
        self.frameInButton.buttonClicked.connect(self.set_frame_in)
        self.frameOutButton.buttonClicked.connect(self.set_frame_out)
        self.lockRangeButton.buttonClicked.connect(self.set_custom_io)

    def load_capture(self, capFile):
        self.cap = cv2.VideoCapture(capFile)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.frameNum = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.cache_cap(capFile)

        self.fpsEdit.set_origin_fps(self.fps)
        self.frameInEdit.setText(str(1))
        self.frameOutEdit.setText(str(self.frameNum))
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
        # self.next_frame()

    def cache_cap(self, capFile):
        frameList = get_frame_list(1, self.frameNum)
        # print frameList
        self.cacheJobs = []
        for index, frameRange in enumerate(frameList):
            cacheThread = CacheThread(capFile, frameIn=frameRange[0], frameOut=frameRange[1])
            cacheThread.set_index(index)
            cacheThread.cacheDone.connect(self.cache_done)
            cacheThread.cacheFrame.connect(self.cache_frame)
            self.cacheJobs.append(cacheThread)
        for cacheThread in self.cacheJobs:
            cacheThread.start()

    def cache_frame(self):
        # print "cache_frame"
        self.cacheFrames.update(self.sender().cacheFrames)
        self.playSlider.set_cache(self.sender().index, self.sender().cacheFrames.keys())

    def cache_done(self):
        self.cacheFrames.update(self.sender().cacheFrames)
        self.playSlider.set_cache(self.sender().index, self.sender().cacheFrames.keys())
        if len(self.cacheFrames.keys()) == self.frameNum:
            print "cache done"
            self.cacheDone = True
            self.cap.release()

    def change_fps(self):
        self.fps = self.fpsEdit.currentFps
        # print self.fps

    def change_frame_in(self, frameIn):
        self.customFrameIn = frameIn
        self.set_custom_io()

    def change_frame_out(self, frameOut):
        self.customFrameOut = frameOut
        self.set_custom_io()

    def set_frame_in(self):
        if not self.lockRangeButton.status:
            self.lockRangeButton.set_status(1)
        self.change_frame_in(self.playSlider.value())
        if self.lockRange:
            self.playSlider.set_mark_in(self.customFrameIn)

    def set_frame_out(self):
        if not self.lockRangeButton.status:
            self.lockRangeButton.set_status(1)
        self.change_frame_out(self.playSlider.value())
        if self.lockRange:
            self.playSlider.set_mark_out(self.customFrameOut)

    def set_custom_io(self):
        self.lockRange = self.lockRangeButton.status
        if self.lockRange:
            self.playSlider.set_mark_visible(True)
            self.frameIn = self.customFrameIn
            self.frameOut = self.customFrameOut
        else:
            self.playSlider.set_mark_visible(False)
            self.frameIn = 1
            self.frameOut = self.frameNum


    def play_backward(self):
        if self.cacheDone:
            self.stop_forward()
            self.playBackwardButton.setVisible(False)
            self.stopBackwardButton.setVisible(True)
            self.playThread.set_fps(self.fps)
            self.playThread.set_status("running", direction=-1)

    def stop_backward(self):
        if self.cacheDone:
            self.playThread.set_status("stop", direction=-1)
            self.playBackwardButton.setVisible(True)
            self.stopBackwardButton.setVisible(False)

    def play_forward(self):
        # print "play forward"
        self.stop_backward()
        self.playForwardButton.setVisible(False)
        self.stopForwardButton.setVisible(True)
        self.playThread.set_fps(self.fps)
        self.playThread.set_status("running")

    def stop_forward(self):
        # print "stop forward"
        self.playThread.set_status("stop")
        self.playForwardButton.setVisible(True)
        self.stopForwardButton.setVisible(False)

    def last_frame(self):
        # print self.currentFrame
        self.set_frame(self.currentFrame-1)

    def skip_forward(self):
        self.set_frame(self.currentFrame + int(self.skipStepsEdit.text()))

    def skip_backward(self):
        self.set_frame(self.currentFrame - int(self.skipStepsEdit.text()))

    def manual_frame(self):
        # print self.playSlider.value()
        # print time.time() - self.manualStart
        if time.time() - self.manualStart >= 1.0 / MAX_REFRESH_FPS:
            self.set_frame(self.playSlider.value())
            self.manualStart = time.time()

    def frame_edit_changed(self):
        self.currentFrameEdit.editingFinished.disconnect(self.frame_edit_changed)
        self.set_frame(int(self.currentFrameEdit.text()))
        self.currentFrameEdit.editingFinished.connect(self.frame_edit_changed)

    def set_frame(self, frame):
        # print frame
        if frame < 1:
            frame = self.frameNum
        if frame > self.frameNum:
            frame = 1
        if frame in self.cacheFrames:
            self.currentFrame = frame
            pixmap = convert_img_from_string(self.cacheFrames[frame])
            self.viewLabel.setPixmap(pixmap)
            self.refresh_ui()
        else:
            self.currentFrame = min(frame - 1, 0)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
            self.next_frame()


    def next_frame(self, direction=1, step=1):
        realStep = direction * step
        if not self.cacheDone:
            # cached ?
            currentFrame = self.currentFrame + realStep
            # print currentFrame
            if currentFrame > self.frameOut and direction == 1:
                currentFrame = self.frameIn
            if currentFrame < self.frameIn and direction == -1:
                currentFrame = self.frameOut
            if currentFrame in self.cacheFrames:
                self.currentFrame = currentFrame
                # self.viewLabel.setPixmap(self.cacheFrames[self.currentFrame])
                self.viewLabel.setPixmap(convert_img_from_string(self.cacheFrames[self.currentFrame]))
                self.refresh_ui()
            else:
                self.ret, self.frame = self.cap.read()
                self.currentFrame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                if self.ret:
                    pixmap = convert_img_from_frame(self.frame)
                    self.viewLabel.setPixmap(pixmap)
                    if self.currentFrame == self.frameNum:
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.refresh_ui()

        else:
            self.currentFrame = self.currentFrame + realStep
            if self.currentFrame > self.frameOut and direction == 1:
                self.currentFrame = self.frameIn
            if self.currentFrame < self.frameIn and direction == -1:
                self.currentFrame = self.frameOut
            # self.viewLabel.setPixmap(self.cacheFrames[self.currentFrame])
            self.viewLabel.setPixmap(convert_img_from_string(self.cacheFrames[self.currentFrame]))
            self.refresh_ui()

    def refresh_ui(self):
        self.currentFrameEdit.setText(str(self.currentFrame))
        self.playSlider.valueChanged.disconnect(self.manual_frame)
        self.playSlider.setValue(self.currentFrame)
        self.playSlider.valueChanged.connect(self.manual_frame)

    def deleteLater(self):
        super(Panel, self).deleteLater()
        # print "deleteLater"
        self.clearLayout(self.masterLayout)

    def clearLayout(self, layout):
        if layout != None:
            # print "clear", layout.count()
            while layout.count():
                child = layout.takeAt(0)
                # print child
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    def resizeEvent(self, QResizeEvent):
        super(Panel, self).resizeEvent(QResizeEvent)
        currentW = self.viewWidget.width()
        currentH = self.viewWidget.height()
        if currentH > 0:
            if currentW / float(currentH) > self.capRatio:
                h = currentH
                w = h * self.capRatio
            else:
                w = currentW
                h = w / self.capRatio
            self.viewLabel.resize(w, h)
            self.viewLabel.move((currentW - w) / 2, (currentH - h) / 2)


class LineEdit(QLineEdit):
    def __init__(self, text=""):
        super(LineEdit, self).__init__()

        self.setFixedHeight(30)
        self.setText(text)
        self.setAlignment(Qt.AlignHCenter)


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
        self.cacheList = [[]] * CACHE_SEGMENTS

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
        for cacheValue in self.cacheList:
            if len(cacheValue) != 0:
                cacheValueIn = self.get_percent(cacheValue[0])*self.width()
                cacheValueOut = self.get_percent(cacheValue[-1] + 1)*self.width()
                painter.drawLine(QLine(QPoint(cacheValueIn, self.height()/2+5), QPoint(cacheValueOut, self.height()/2+5)))

    def set_cache(self, index, valueList):
        # print index, valueList
        valueList.sort()
        self.cacheList[index] = valueList
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


class LabelButton1(QLabel):
    buttonClicked = Signal()
    def __init__(self, icon=None, text=None):
        super(LabelButton1, self).__init__()

        self.icon = icon
        if self.icon:
            self.setToolTip("%s" % self.icon)
            self.imagePixmap = resource.get_pixmap('player', '%s.png' % (self.icon), scale=Icon_Size)
            self.imageHoverPixmap = resource.get_pixmap('player', '%s_hover.png' % (self.icon), scale=Icon_Size)
            self.imageClickedPixmap = resource.get_pixmap('player', '%s_clicked.png' % (self.icon), scale=Icon_Size)
            self.setPixmap(self.imagePixmap)

        self.textStr = text
        self.textNormalStr = "<font color=white>%s</font>" % text
        self.textHoverStr = "<font color=#00A2FF>%s</font>" % text
        self.textClickedStr = "<font color=#0076BA>%s</font>" % text
        if self.textStr:
            self.setFixedWidth(Icon_Size)
            self.setAlignment(Qt.AlignCenter)
            self.setText(self.textNormalStr)

    def enterEvent(self, event):
        if self.icon:
            self.setPixmap(self.imageHoverPixmap)
        if self.textStr:
            self.setText(self.textHoverStr)

    def leaveEvent(self, event):
        if self.icon:
            self.setPixmap(self.imagePixmap)
        if self.textStr:
            self.setText(self.textNormalStr)

    def mousePressEvent(self, event):
        if self.icon:
            self.setPixmap(self.imageClickedPixmap)
        if self.textStr:
            self.setText(self.textClickedStr)

    def mouseReleaseEvent(self, event):
        self.buttonClicked.emit()
        if self.icon:
            self.setPixmap(self.imageHoverPixmap)
        if self.textStr:
            self.setText(self.textHoverStr)


class LabelButton2(QLabel):
    buttonClicked = Signal()
    def __init__(self, icon=None, text=None):
        super(LabelButton2, self).__init__()

        self.status = 0

        self.icon = icon
        if self.icon:
            self.setToolTip("%s" % self.icon)
            self.imagePixmap = resource.get_pixmap('player', '%s.png' % (self.icon), scale=Icon_Size)
            self.imageHoverPixmap = resource.get_pixmap('player', '%s_hover.png' % (self.icon), scale=Icon_Size)
            self.imageClickedPixmap = resource.get_pixmap('player', '%s_clicked.png' % (self.icon), scale=Icon_Size)
            self.setPixmap(self.imagePixmap)

        self.textStr = text
        self.textNormalStr = "<font color=white>%s</font>" % text
        self.textHoverStr = "<font color=#00A2FF>%s</font>" % text
        self.textClickedStr = "<font color=#0076BA>%s</font>" % text
        if self.textStr:
            self.setText(self.textNormalStr)

    def enterEvent(self, event):
        if self.icon:
            self.setPixmap(self.imageHoverPixmap)
        if self.textStr:
            self.setText(self.textHoverStr)

    def leaveEvent(self, event):
        self.update_status()

    def mousePressEvent(self, event):
        if self.icon:
            self.setPixmap(self.imageClickedPixmap)
        if self.textStr:
            self.setText(self.textClickedStr)

    def mouseReleaseEvent(self, event):
        self.status = 1 - self.status
        self.buttonClicked.emit()
        if self.icon:
            self.setPixmap(self.imageHoverPixmap)
        if self.textStr:
            self.setText(self.textHoverStr)

    def set_status(self, status):
        self.status = status
        self.update_status()

    def update_status(self):
        if self.icon:
            if self.status == 1:
                self.setPixmap(self.imageClickedPixmap)
            else:
                self.setPixmap(self.imagePixmap)
        if self.textStr:
            self.setText(self.textNormalStr)


class FpsLineEdit(QLineEdit):
    fpsChanged = Signal()
    def __init__(self, parent=None):
        super(FpsLineEdit, self).__init__(parent)

        self.toolButton = QToolButton(self)
        self.toolButton.setIcon(resource.get_qicon("player", "action01.png"))
        self.toolButton.setPopupMode(QToolButton.InstantPopup)
        self.toolButton.setArrowType(Qt.NoArrow)
        self.toolButton.setCursor(Qt.ArrowCursor)
        self.toolButton.setStyleSheet("""
            QToolButton::menu-indicator { image: None; }
            QToolButton{border: 0px; padding: 0px;}
        """)
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        buttonSize = self.toolButton.sizeHint()
        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth * 2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth * 2 + 2))

        self.originFps = 0
        self.currentFps = 0

        self.textChanged.connect(self.manual_fps)


    def set_origin_fps(self, fps):
        self.textChanged.disconnect(self.manual_fps)
        self.originFps = fps
        self.currentFps = fps
        self.setText("%s*" % fps)
        self.set_actions()
        self.textChanged.connect(self.manual_fps)
        self.fpsChanged.emit()

    def set_actions(self):
        self.fpsList = [0.25,
                        0.5,
                        2,
                        6,
                        8,
                        12,
                        24,
                        25,
                        60]
        if self.originFps not in self.fpsList:
            self.fpsList.append(self.originFps)
        self.fpsList.sort()
        self.fpsStrList = []
        for i in self.fpsList:
            if self.fpsList.index(i) < 3:
                fpsStr = "%sx" % i
            elif i == self.originFps:
                fpsStr = "%s*" % i
            else:
                fpsStr = "%s" % i
            fpsAction = QAction(fpsStr, self)
            setattr(fpsAction, "fpsFloat", i)
            fpsAction.triggered.connect(self.set_fps)
            self.toolButton.addAction(fpsAction)


    def set_fps(self):
        self.textChanged.disconnect(self.manual_fps)
        fpsFloat = self.sender().fpsFloat
        fpsText = str(self.sender().text())
        if fpsText.find("x") != -1:
            self.currentFps = self.originFps * fpsFloat
        else:
            self.currentFps = fpsFloat
        # print self.currentFps
        self.setText(fpsText)
        self.textChanged.connect(self.manual_fps)
        self.fpsChanged.emit()

    def manual_fps(self):
        fpsText = str(self.text())
        if fpsText.find("x") != -1:
            self.currentFps = self.originFps * float(fpsText.replace("x", ""))
        else:
            self.currentFps = float(fpsText)
        # print self.currentFps
        self.fpsChanged.emit()


    def resizeEvent(self, event):
        buttonSize = self.toolButton.sizeHint()
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.toolButton.move(self.rect().right() - frameWidth - buttonSize.width(),
                             (self.rect().bottom() - buttonSize.height() + 1) / 2)
        super(FpsLineEdit, self).resizeEvent(event)


class PlayThread(QThread):
    refresh = Signal(int, int)
    def __init__(self):
        super(PlayThread, self).__init__()
        self.fps = 1
        self.status = "stop" # "running
        self.direction = 1
        self.step = 1

    def set_fps(self, fps):
        self.step = 1
        self.fps = float(fps)
        if fps > MAX_REFRESH_FPS:
            self.step = int(math.ceil(float(fps)/MAX_REFRESH_FPS))
            self.fps = self.fps/self.step
        # print self.fps

    def set_status(self, status, direction=1): # 1:forward, -1:backward
        self.status = status
        self.direction = direction
        if status == "running":
            self.start()
        else:
            self.terminate()

    def run(self):
        if self.status == "running":
            while(1):
                self.refresh.emit(self.direction, self.step)
                time.sleep(1/self.fps)
        else:
            pass




if __name__ == "__main__":
    app = QApplication(sys.argv)
    # panel = Test()
    panel = Panel()
    panel.show()
    app.exec_()
