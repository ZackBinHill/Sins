# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 3/31/2018

from cv2 import *
import cv2

if cv2.__version__.split(".")[0] == "2":
    CAPtureFromFile = cv.CaptureFromFile
    CAP_PROP_FPS = cv.CV_CAP_PROP_FPS
    CAP_PROP_FRAME_COUNT = cv.CV_CAP_PROP_FRAME_COUNT
    CAP_PROP_POS_FRAMES = cv.CV_CAP_PROP_POS_FRAMES
    CAP_PROP_FRAME_WIDTH = cv.CV_CAP_PROP_FRAME_WIDTH
    CAP_PROP_FRAME_HEIGHT = cv.CV_CAP_PROP_FRAME_HEIGHT