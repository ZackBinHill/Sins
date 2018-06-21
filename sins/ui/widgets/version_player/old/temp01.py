from PyQt4.QtCore import *
from PyQt4.QtGui import *
Signal = pyqtSignal
import os
import sys
import time
import cv2
import numpy


ThisFolder = os.path.dirname(__file__)
Icons_Folder = "%s/icons" % os.path.dirname(__file__)
Icon_Size = 24


class Test(QWidget):
    def __init__(self):
        super(Test, self).__init__()

        a = time.time()
        # pixmap = QPixmap("tmp/test.png")
        pixmap = QPixmap("tmp/test.jpg")
        # pixmap = QPixmap("tmp/test.bmp")
        # frame = cv2.imread("tmp/test.png")
        # frame = cv2.imread("tmp/test.jpg")
        b = time.time()
        print b - a

        self.load_capture("%s/test2.mp4" % ThisFolder)


    def load_capture(self, capFile):
        self.cache_cap(capFile)

    def cache_cap(self, capFile):
        self.cacheThread = CacheThread(capFile)
        self.cacheThread.start()




class CacheThread(QThread):
    cacheDone = Signal()
    cacheFrame = Signal()
    def __init__(self, capFile):
        super(CacheThread, self).__init__()

        self.cap = cv2.VideoCapture(capFile)
        self.frameNum = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

        self.cacheFrames = {}



    def run(self):

        self.cacheFrames = {}
        for i in range(self.frameNum):
            ret, frame = self.cap.read()
            if ret:
                a = time.time()
                # frame = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_AREA)
                # frame = cv2.resize(frame, (960, 540), interpolation=cv2.INTER_AREA)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                img_code = numpy.array(imgencode)
                imgdata = img_code.tostring()

                b = time.time()

                img_decode = numpy.fromstring(imgdata, numpy.uint8)
                frame = cv2.imdecode(img_decode, 1)

                height, width, bytesPerComponent = frame.shape
                bytesPerLine = 3 * width
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
                QImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(QImg)

                if i == 10:
                    # cv2.imwrite("tmp/test.png", frame)
                    # cv2.imwrite("tmp/test.jpg", frame)
                    # cv2.imwrite("tmp/test.bmp", frame)
                    # print frame
                    print sys.getsizeof(frame)
                    print sys.getsizeof(imgdata)

                    c = time.time()
                    # print b - a
                    # print c - b

                # self.cacheFrames[i+1] = pixmap
                # self.cacheFrames[i+1] = frame
                self.cacheFrames[i+1] = imgdata
                # self.cacheFrames[i+1] = imgdecode
                # self.cacheFrames.update({i+1:pixmap})
                if i % 10 == 0:
                    self.cacheFrame.emit()

        self.cacheDone.emit()
        self.cap.release()
        # print sys.getsizeof(self.cacheFrames)
        # print sys.getsizeof(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = Test()
    # panel = Panel()
    panel.show()
    app.exec_()