# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 1/16/2018




'''
import cv2 as cv

img = cv.imread("test.png")
cv.namedWindow("Image")
cv.imshow("Image",img)
cv.waitKey(0)
cv.destroyAllWindows()






import cv2
import numpy as np

cap = cv2.VideoCapture("test.mp4")
while(1):
    # get a frame
    ret, frame = cap.read()
    # show a frame
    cv2.imshow("capture", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


'''


'''

import cv2.cv as cv

capture = cv.CaptureFromFile('test.mp4')

nbFrames = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT))

# CV_CAP_PROP_FRAME_WIDTH Width of the frames in the video stream
# CV_CAP_PROP_FRAME_HEIGHT Height of the frames in the video stream

fps = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FPS)

wait = int(1 / fps * 1000 / 1)

duration = (nbFrames * fps) / 1000

print 'Num. Frames = ', nbFrames
print 'Frame Rate = ', fps, 'fps'
print 'Duration = ', duration, 'sec'

for f in xrange(nbFrames):
    frameImg = cv.QueryFrame(capture)
    print cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_POS_FRAMES)
    cv.ShowImage("The Video", frameImg)
    cv.WaitKey(wait)
'''




from PyQt4.QtCore import *
from PyQt4.QtGui import *
Signal = pyqtSignal
import os
import sys
import time
import cv2


Icons_Folder = "%s/icons" % os.path.dirname(__file__)
Icon_Size = 24


class Panel(QWidget):
    def __init__(self):
        super(Panel, self).__init__()


        self.initUi()

        self.cap = None
        self.fps = 1
        self.frameNum = 0
        self.frameIn = 1
        self.frameOut = 1
        self.currentFrame = 1
        self.playThread = PlayThread()
        self.playThread.refresh.connect(self.next_frame)
        self.playThread.start()

        self.set_signal()

        self.load_capture("test.mov")
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
        self.playSlider = QSlider(Qt.Horizontal)
        self.frameOutEdit = LineEdit("100")
        self.frameOutEdit.setMaximumWidth(50)
        self.sliderLayout.addWidget(self.frameInEdit)
        self.sliderLayout.addWidget(self.playSlider)
        self.sliderLayout.addWidget(self.frameOutEdit)

        self.buttonLayout = QHBoxLayout()
        self.fpsEdit = FpsLineEdit()
        self.fpsEdit.setMaximumWidth(50)
        self.stopForwardButton = LabelButton1("stop")
        self.stopForwardButton.setVisible(False)
        self.playForwardButton = LabelButton1("play_forward")
        self.lastFrameButton = LabelButton1("last_frame")
        self.nextFrameButton = LabelButton1("next_frame")
        self.skipBackwardButton = LabelButton1("skip_backward")
        self.skipForwardButton = LabelButton1("skip_forward")
        self.currentFrameEdit = LineEdit()
        self.currentFrameEdit.setMaximumWidth(50)
        self.skipStepsEdit = LineEdit("10")
        self.skipStepsEdit.setMaximumWidth(50)

        self.buttonLayout.addWidget(self.fpsEdit)
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.lastFrameButton)
        self.buttonLayout.addWidget(self.currentFrameEdit)
        self.buttonLayout.addWidget(self.stopForwardButton)
        self.buttonLayout.addWidget(self.playForwardButton)
        self.buttonLayout.addWidget(self.nextFrameButton)
        self.buttonLayout.addSpacing(50)
        self.buttonLayout.addWidget(self.skipBackwardButton)
        self.buttonLayout.addWidget(self.skipStepsEdit)
        self.buttonLayout.addWidget(self.skipForwardButton)
        self.buttonLayout.addStretch()

        self.masterLayout.addLayout(self.capTitleLayout)
        self.masterLayout.addWidget(self.viewWindow)
        self.masterLayout.addLayout(self.sliderLayout)
        self.masterLayout.addLayout(self.buttonLayout)
        self.setLayout(self.masterLayout)

        styleText = open("style.txt").read()
        self.setStyleSheet(styleText)

    def set_signal(self):
        self.fpsEdit.textChanged.connect(self.change_fps)
        self.playSlider.valueChanged.connect(self.manual_frame)
        self.playForwardButton.buttonClicked.connect(self.play_forward)
        self.stopForwardButton.buttonClicked.connect(self.stop_forward)
        self.nextFrameButton.buttonClicked.connect(self.next_frame)
        self.lastFrameButton.buttonClicked.connect(self.last_frame)
        self.skipBackwardButton.buttonClicked.connect(self.skip_backward)
        self.skipForwardButton.buttonClicked.connect(self.skip_forward)

    def load_capture(self, capFile):
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
        self.next_frame()

    def change_fps(self):
        self.fps = self.fpsEdit.currentFps

    def play_forward(self):
        # print "play forward"
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
        self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame-1)
        self.next_frame()

    def next_frame(self):
        # print self.cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        # a = time.time()
        self.ret, self.frame = self.cap.read()
        # b = time.time()
        # print b - a
        self.currentFrame = int(self.cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))
        if self.ret:
            height, width, bytesPerComponent = self.frame.shape
            bytesPerLine = 3 * width
            cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB, self.frame)
            QImg = QImage(self.frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(QImg)
            self.viewWindow.setPixmap(pixmap)
            # self.currentFrame = self.cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
            if self.currentFrame == self.frameNum:
                self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)
            self.currentFrameEdit.setText(str(self.currentFrame))
            self.playSlider.valueChanged.disconnect(self.manual_frame)
            self.playSlider.setValue(self.currentFrame)
            self.playSlider.valueChanged.connect(self.manual_frame)


class LineEdit(QLineEdit):
    def __init__(self, text=""):
        super(LineEdit, self).__init__()

        self.setText(text)
        self.setAlignment(Qt.AlignHCenter)


class LabelButton1(QLabel):
    buttonClicked = Signal()
    def __init__(self, name):
        super(LabelButton1, self).__init__()

        self.name = name
        self.setToolTip("%s" % self.name)
        self.imageFile = '%s/%s.png' % (Icons_Folder, self.name)
        self.imageHoverFile = '%s/%s_hover.png' % (Icons_Folder, self.name)
        self.imageClickedFile = '%s/%s_clicked.png' % (Icons_Folder, self.name)
        self.setPixmap(QPixmap(self.imageFile).
                       scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def enterEvent(self, event):
        self.setPixmap(QPixmap(self.imageHoverFile).
                       scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def leaveEvent(self, event):
        self.setPixmap(QPixmap(self.imageFile).
                       scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        self.setPixmap(QPixmap(self.imageClickedFile).
                       scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mouseReleaseEvent(self, event):
        self.buttonClicked.emit()
        self.setPixmap(QPixmap(self.imageHoverFile).
                       scaled(Icon_Size, Icon_Size, Qt.KeepAspectRatio, Qt.SmoothTransformation))


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
            if i < 1:
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
        fpsText = self.sender().text()
        if fpsFloat < 1:
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





class PlayThread(QThread):
    refresh = Signal()
    def __init__(self):
        super(PlayThread, self).__init__()
        self.fps = 1
        self.status = "stop" # "running

    def set_fps(self, fps):
        self.fps = float(fps)

    def set_status(self, status):
        self.status = status

    def run(self):
        while(1):
            if self.status == "running":
                self.refresh.emit()
                time.sleep(1/self.fps)
            else:
                pass




app = QApplication(sys.argv)
panel = Panel()
panel.show()
app.exec_()
