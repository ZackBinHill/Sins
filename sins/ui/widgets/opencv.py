# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 3/31/2018

import sys
import os
import numpy
import time
import sins.module.cv as cv2
from sins.module.sqt import *
from sins.utils.const import VIDEO_EXT, IMG_EXT
from sins.utils.log import log_cost_time


def convert_img_from_frame(frame):
    height, width, bytesPerComponent = frame.shape
    bytesPerLine = 3 * width
    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
    QImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(QImg)
    return pixmap


def convert_frame_from_string(imgdata):
    img_decode = numpy.fromstring(imgdata, numpy.uint8)
    frame = cv2.imdecode(img_decode, cv2.IMREAD_COLOR)
    return frame


def convert_img_from_string(imgdata):
    # img_decode = numpy.fromstring(imgdata, numpy.uint8)
    frame = convert_frame_from_string(imgdata)
    # height, width, bytesPerComponent = frame.shape
    # bytesPerLine = 3 * width
    # cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
    # QImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
    pixmap = convert_img_from_frame(frame)
    return pixmap


def convert_string_from_frame(frame, w=None, h=None, quality=90):
    if w is not None and h is not None:
        frame = cv2.resize(frame, (w, h))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
    img_code = numpy.array(imgencode)
    imgdata = img_code.tostring()
    return imgdata


class CacheThread(QThread):
    cacheDone = Signal()
    cacheFrame = Signal()

    def __init__(self, capFile,
                 cap=None,
                 frameIn=1,
                 frameOut=1,
                 step=1,
                 resize=1,
                 fixwidth=None,
                 readcache=False,
                 tocache=False):
        super(CacheThread, self).__init__()

        self.capFile = capFile
        self.step = step
        self.resizeRatio = resize
        self.fixWidth = fixwidth
        self.readcache = readcache
        self.tocache = tocache

        self.index = 0

        if cap is None:
            self.cap = cv2.VideoCapture(capFile)
        else:
            self.cap = cap
        self.frameIn = frameIn
        self.frameOut = frameOut
        self.frameNum = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameW = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frameH = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.cacheFrames = {}

    def set_index(self, index):
        self.index = index

    @log_cost_time
    def run(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frameIn - 1)
        self.cacheFrames = {}

        self.cacheFile = os.path.abspath(self.capFile) + ".thumbnail"

        if os.path.exists(self.cacheFile) and self.readcache:
            try:
                f = open(self.cacheFile, "rb")
                data = f.read()
                f.close()
                frames = data.split("##########")
                length = len(frames[1:])
                if length == len(range(self.frameIn, self.frameOut + 1, self.step)) * 2:
                    for i in range(1, length, 2):
                        self.cacheFrames[int(frames[i])] = frames[i + 1]
                    # print self.cacheFrames.keys()
                else:
                    self.cache_frames()
            except:
                self.cache_frames()
        else:
            self.cache_frames()

        self.cacheDone.emit()
        self.cap.release()

    def cache_frames(self):
        if self.tocache:
            f = open(self.cacheFile, 'wb')
        for i in range(self.frameIn, self.frameOut + 1):
            ret, frame = self.cap.read()
            if i in range(self.frameIn, self.frameOut + 1, self.step):
                if ret:
                    if self.fixWidth is None:
                        w = int(self.frameW * self.resizeRatio)
                        h = int(self.frameH * self.resizeRatio)
                    else:
                        w = self.fixWidth
                        h = int(self.fixWidth * self.frameH / self.frameW)
                    # frame = cv2.resize(frame, (w, h))
                    # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                    # result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                    # img_code = numpy.array(imgencode)
                    # imgdata = img_code.tostring()
                    imgdata = convert_string_from_frame(frame, w, h)

                    self.cacheFrames[i] = imgdata
                    if i % 10 == 0:
                        self.cacheFrame.emit()

                    if self.tocache:
                        f.write("##########%s##########" % i)
                        f.write(imgdata)
        if self.tocache:
            f.close()


class ReadThread(QThread):
    readDone = Signal(object)
    def __init__(self,
                 readFile,
                 cap=None,
                 frame=1,
                 fixwidth=None,
                 readcache=True
                 ):
        super(ReadThread, self).__init__()

        self.readFile = readFile
        self.fixWidth = fixwidth
        self.readcache = readcache
        if os.path.splitext(readFile)[1] in VIDEO_EXT:
            if cap is None:
                self.cap = cv2.VideoCapture(readFile)
            else:
                self.cap = cap
            self.frame = frame

        self.cacheFile = os.path.abspath(self.readFile) + ".thumbnail"

    def run(self):
        if os.path.splitext(self.readFile)[1] in VIDEO_EXT:
            if os.path.exists(self.cacheFile) and self.readcache:
                try:
                    f = open(self.cacheFile, "rb")
                    data = f.read()
                    f.close()
                    frames = data.split("##########")
                    if str(self.frame) in frames:
                        index = frames.index(str(self.frame))
                        imgdata = frames[index + 1]
                        self.readDone.emit(convert_frame_from_string(imgdata))
                    else:
                        self.read_from_video_file()
                except:
                    self.read_from_video_file()
            else:
                self.read_from_video_file()

        elif os.path.splitext(self.readFile)[1] in IMG_EXT:
            if os.path.exists(self.cacheFile) and self.readcache:
                try:
                    f = open(self.cacheFile, "rb")
                    data = f.read()
                    f.close()
                    self.readDone.emit(convert_frame_from_string(data))
                except:
                    self.read_from_image_file()
            else:
                self.read_from_image_file()
                self.cache_image()

    def read_from_video_file(self):
        frameNum = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, self.frame - 1)
        ret, frame = self.cap.read()
        if ret:
            self.readDone.emit(frame)
        self.cap.release()

    def read_from_image_file(self):
        img = cv2.imread(self.readFile)
        self.readDone.emit(img)

    def cache_image(self):
        f = open(self.cacheFile, 'wb')
        img = cv2.imread(self.readFile)
        height, width, bytesPerComponent = img.shape
        if self.fixWidth is not None:
            w = self.fixWidth
            h = int(self.fixWidth * height / width)
        else:
            w = width
            h = height
        imgdata = convert_string_from_frame(img, w, h)
        f.write(imgdata)
        f.close()


if __name__ == "__main__":
    from sins.test.test_res import TestMov
    app = QApplication(sys.argv)
    capFile = TestMov("test.mp4")
    cacheThread = CacheThread(capFile, cap=None, frameIn=1, frameOut=1180, step=1, resize=1, fixwidth=None, readcache=False, tocache=True)
    cacheThread.start()
    app.exec_()