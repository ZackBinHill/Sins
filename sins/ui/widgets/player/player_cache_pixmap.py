# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 1/26/2018



from PyQt4.QtCore import *
from PyQt4.QtGui import *
Signal = pyqtSignal
import os
import sys
import time
import cv2

ThisFolder = os.path.dirname(__file__)
Icons_Folder = "%s/icons" % os.path.dirname(__file__)
Icon_Size = 24


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

        # self.load_capture("test.mov")
        # self.load_capture("test.mp4")
        self.load_capture("%s/test2.mp4" % ThisFolder)
        # self.cap = cv2.cv.CaptureFromFile('test.mp4')


    def initUi(self):
        self.masterLayout = QVBoxLayout()
        self.label = QLabel()

        self.capTitleLayout = QHBoxLayout()
        self.capTitle = QLabel("test_v001")
        self.capTitleLayout.addWidget(self.capTitle)

        self.viewWindow = QLabel()
        # self.viewWindow.setFixedSize(640, 360)
        # self.viewWindow.setPixmap(QPixmap("test01.png"))

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
        self.masterLayout.addWidget(self.viewWindow)
        self.masterLayout.addLayout(self.sliderLayout)
        self.masterLayout.addLayout(self.buttonLayout)
        self.setLayout(self.masterLayout)

        styleText = open("%s/style.css" % ThisFolder).read()
        self.setStyleSheet(styleText)

    def set_signal(self):
        self.fpsEdit.textChanged.connect(self.change_fps)
        self.playSlider.valueChanged.connect(self.manual_frame)
        self.playForwardButton.buttonClicked.connect(self.play_forward)
        self.stopForwardButton.buttonClicked.connect(self.stop_forward)
        self.playBackwardButton.buttonClicked.connect(self.play_backward)
        self.stopBackwardButton.buttonClicked.connect(self.stop_backward)
        self.nextFrameButton.buttonClicked.connect(self.next_frame)
        self.lastFrameButton.buttonClicked.connect(self.last_frame)
        self.skipBackwardButton.buttonClicked.connect(self.skip_backward)
        self.skipForwardButton.buttonClicked.connect(self.skip_forward)
        self.frameInButton.buttonClicked.connect(self.set_frame_in)
        self.frameOutButton.buttonClicked.connect(self.set_frame_out)
        self.lockRangeButton.buttonClicked.connect(self.set_custom_io)


    def load_capture(self, capFile):
        self.cache_cap(capFile)
        self.cap = cv2.VideoCapture(capFile)
        self.fps = int(self.cap.get(cv2.cv.CV_CAP_PROP_FPS))
        self.frameNum = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        self.fpsEdit.set_origin_fps(self.fps)
        self.frameInEdit.setText(str(1))
        self.frameOutEdit.setText(str(self.frameNum))
        self.frameIn = 1
        self.frameOut = self.frameNum
        self.playSlider.setMinimum(1)
        self.playSlider.setMaximum(self.frameNum)
        self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
        self.currentFrame = 1
        self.next_frame()

    def cache_cap(self, capFile):
        self.cacheThread = CacheThread(capFile)
        self.cacheThread.cacheDone.connect(self.cache_done)
        self.cacheThread.cacheFrame.connect(self.cache_frame)
        self.cacheThread.start()

    def cache_frame(self):
        # print "cache_frame"
        self.cacheFrames.update(self.cacheThread.cacheFrames)
        self.playSlider.set_cache(len(self.cacheFrames.keys()))

    def cache_done(self):
        print "cache done"
        self.cacheDone = True
        self.cacheFrames = self.cacheThread.cacheFrames
        self.cacheThread.cacheFrames = {}
        self.playSlider.set_cache(len(self.cacheFrames.keys()))
        self.cap.release()

    def set_first_frame(self):
        self.ret, self.frame = self.cap.read()
        if self.ret:
            height, width, bytesPerComponent = self.frame.shape
            bytesPerLine = 3 * width
            cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB, self.frame)
            QImg = QImage(self.frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(QImg)
            self.viewWindow.setPixmap(pixmap)

    def change_fps(self):
        self.fps = self.fpsEdit.currentFps

    def set_frame_in(self):
        self.customFrameIn = self.playSlider.value()
        self.set_custom_io()
        if self.lockRange:
            self.playSlider.set_mark_in(self.customFrameIn)

    def set_frame_out(self):
        self.customFrameOut = self.playSlider.value()
        self.set_custom_io()
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
        self.set_frame(self.currentFrame-1)

    def skip_forward(self):
        self.set_frame(self.currentFrame + int(self.skipStepsEdit.text()))

    def skip_backward(self):
        self.set_frame(self.currentFrame - int(self.skipStepsEdit.text()))

    def manual_frame(self):
        # print self.playSlider.value()
        self.set_frame(self.playSlider.value())

    def set_frame(self, frame):
        if frame < 1:
            frame = self.frameNum
        if frame > self.frameNum:
            frame = 1
        if frame in self.cacheFrames:
            self.currentFrame = frame
            self.viewWindow.setPixmap(self.cacheFrames[frame])
            self.refresh_ui()
        else:
            self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame - 1)
            self.next_frame()


    def next_frame(self, direction=1):
        if not self.cacheDone:
            # cached ?
            currentFrame = self.currentFrame + direction
            if currentFrame > self.frameOut and direction == 1:
                currentFrame = self.frameIn
            if currentFrame < self.frameIn and direction == -1:
                currentFrame = self.frameOut
            if currentFrame in self.cacheFrames:
                self.currentFrame = currentFrame
                self.viewWindow.setPixmap(self.cacheFrames[self.currentFrame])
                self.refresh_ui()
            else:
                self.ret, self.frame = self.cap.read()
                self.currentFrame = int(self.cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))
                if self.ret:
                    pixmap = self.convert_img(self.frame)
                    self.viewWindow.setPixmap(pixmap)
                    if self.currentFrame == self.frameNum:
                        self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
                    self.refresh_ui()

        else:
            self.currentFrame = self.currentFrame + direction
            if self.currentFrame > self.frameOut and direction == 1:
                self.currentFrame = self.frameIn
            if self.currentFrame < self.frameIn and direction == -1:
                self.currentFrame = self.frameOut
            self.viewWindow.setPixmap(self.cacheFrames[self.currentFrame])
            self.refresh_ui()

    def refresh_ui(self):
        self.currentFrameEdit.setText(str(self.currentFrame))
        self.playSlider.valueChanged.disconnect(self.manual_frame)
        self.playSlider.setValue(self.currentFrame)
        self.playSlider.valueChanged.connect(self.manual_frame)

    def convert_img(self, frame):
        height, width, bytesPerComponent = frame.shape
        bytesPerLine = 3 * width
        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
        QImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        return pixmap

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

class LineEdit(QLineEdit):
    def __init__(self, text=""):
        super(LineEdit, self).__init__()

        self.setText(text)
        self.setAlignment(Qt.AlignHCenter)


class PlaySlider(QSlider):
    def __init__(self):
        super(PlaySlider, self).__init__()

        self.setOrientation(Qt.Horizontal)
        self.percentIn = 0
        self.percentOut = 1
        self.showMark = False
        self.cacheValue = 0

    def paintEvent(self, QPaintEvent):
        super(PlaySlider, self).paintEvent(QPaintEvent)

        painter = QPainter(self)

        self.draw_mark(painter)
        self.draw_cache(painter)

    def draw_mark(self, painter):
        if self.showMark:
            pen = QPen(QColor(200, 200, 200))
            pen.setWidth(3)
            painter.setPen(pen)
            if self.percentIn != None:
                positionIn = self.percentIn*self.width()+5-10*self.percentIn
                painter.drawLine(QLine(QPoint(positionIn, 0), QPoint(positionIn, 10)))
            if self.percentOut != None:
                positionOut = self.percentOut*self.width()+5-10*self.percentOut
                painter.drawLine(QLine(QPoint(positionOut, 0), QPoint(positionOut, 10)))

    def set_mark_in(self, value):
        self.percentIn = float(value-1)/(self.maximum()-1)
        # print self.percentIn
        self.update()

    def set_mark_out(self, value):
        self.percentOut = float(value-1)/(self.maximum()-1)
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
        self.cacheValue = float(value-1)/(self.maximum()-1)
        self.update()


class LabelButton1(QLabel):
    buttonClicked = Signal()
    def __init__(self, icon=None, text=None):
        super(LabelButton1, self).__init__()

        self.icon = icon
        if self.icon:
            self.setToolTip("%s" % self.icon)
            self.imageFile = '%s/%s.png' % (Icons_Folder, self.icon)
            self.imageHoverFile = '%s/%s_hover.png' % (Icons_Folder, self.icon)
            self.imageClickedFile = '%s/%s_clicked.png' % (Icons_Folder, self.icon)
            self.setPixmap(QPixmap(self.imageFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

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
            self.setPixmap(QPixmap(self.imageHoverFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.textStr:
            self.setText(self.textHoverStr)

    def leaveEvent(self, event):
        if self.icon:
            self.setPixmap(QPixmap(self.imageFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.textStr:
            self.setText(self.textNormalStr)

    def mousePressEvent(self, event):
        if self.icon:
            self.setPixmap(QPixmap(self.imageClickedFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.textStr:
            self.setText(self.textClickedStr)

    def mouseReleaseEvent(self, event):
        self.buttonClicked.emit()
        if self.icon:
            self.setPixmap(QPixmap(self.imageHoverFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
            self.imageFile = '%s/%s.png' % (Icons_Folder, self.icon)
            self.imageHoverFile = '%s/%s_hover.png' % (Icons_Folder, self.icon)
            self.imageClickedFile = '%s/%s_clicked.png' % (Icons_Folder, self.icon)
            self.setPixmap(QPixmap(self.imageFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.textStr = text
        self.textNormalStr = "<font color=white>%s</font>" % text
        self.textHoverStr = "<font color=#00A2FF>%s</font>" % text
        self.textClickedStr = "<font color=#0076BA>%s</font>" % text
        if self.textStr:
            self.setText(self.textNormalStr)

    def enterEvent(self, event):
        if self.icon:
            self.setPixmap(QPixmap(self.imageHoverFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.textStr:
            self.setText(self.textHoverStr)

    def leaveEvent(self, event):
        if self.icon:
            if self.status == 1:
                self.setPixmap(QPixmap(self.imageClickedFile).
                               scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.setPixmap(QPixmap(self.imageFile).
                               scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.textStr:
            self.setText(self.textNormalStr)

    def mousePressEvent(self, event):
        if self.icon:
            self.setPixmap(QPixmap(self.imageClickedFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.textStr:
            self.setText(self.textClickedStr)

    def mouseReleaseEvent(self, event):
        self.status = 1 - self.status
        self.buttonClicked.emit()
        if self.icon:
            self.setPixmap(QPixmap(self.imageHoverFile).
                           scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self.textStr:
            self.setText(self.textHoverStr)


class FpsLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(FpsLineEdit, self).__init__(parent)

        self.toolButton = QToolButton(self)
        self.toolButton.setIcon(QIcon("%s/action01.png" % Icons_Folder))
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


    def set_origin_fps(self, fps):
        self.originFps = fps
        self.currentFps = fps
        self.setText("%s*" % fps)
        self.set_actions()


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
        fpsFloat = self.sender().fpsFloat
        fpsText = str(self.sender().text())
        if fpsText.find("x") != -1:
            self.currentFps = self.originFps * fpsFloat
        else:
            self.currentFps = fpsFloat
        # print self.currentFps
        self.setText(fpsText)

    def resizeEvent(self, event):
        buttonSize = self.toolButton.sizeHint()
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.toolButton.move(self.rect().right() - frameWidth - buttonSize.width(),
                             (self.rect().bottom() - buttonSize.height() + 1) / 2)
        super(FpsLineEdit, self).resizeEvent(event)


class CacheThread(QThread):
    cacheDone = Signal()
    cacheFrame = Signal()
    def __init__(self, capFile):
        super(CacheThread, self).__init__()

        self.cap = cv2.VideoCapture(capFile)
        self.frameNum = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        self.cacheFrames = {}

    def run(self):
        # a = time.time()
        self.cacheFrames = {}
        for i in range(self.frameNum):
            self.ret, self.frame = self.cap.read()
            if self.ret:
                height, width, bytesPerComponent = self.frame.shape
                bytesPerLine = 3 * width
                cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB, self.frame)
                QImg = QImage(self.frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(QImg)
                self.cacheFrames[i+1] = pixmap
                if i % 10 == 0:
                    self.cacheFrame.emit()
        # b = time.time()
        # print b - a
        self.cacheDone.emit()
        self.cap.release()
        self.cacheFrames = {}


class PlayThread(QThread):
    refresh = Signal(int)
    def __init__(self):
        super(PlayThread, self).__init__()
        self.fps = 1
        self.status = "stop" # "running
        self.direction = 1

    def set_fps(self, fps):
        self.fps = float(fps)

    def set_status(self, status, direction=1): # 1:forward, -1:backward
        self.status = status
        self.direction = direction

    def run(self):
        while(1):
            if self.status == "running":
                self.refresh.emit(self.direction)
                time.sleep(1/self.fps)
            else:
                pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = Panel()
    panel.show()
    app.exec_()
