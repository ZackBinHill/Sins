# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/1/2018

import json
import os
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import module.cv as cv2
import numpy

def read_json(jsonFile):
    if os.path.exists(jsonFile):
        with open(jsonFile, "r") as json_file:
            # file_data = json_file.read()
            # print file_data
            # jsonData = eval(file_data)
            # jsonData = json.loads(file_data)
            jsonData = json.load(json_file)
        return jsonData
    else:
        return {}


def write_json(data, jsonFile):
    path = os.path.abspath(jsonFile)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    jsonDic = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), encoding="utf-8", ensure_ascii=False)
    # jsonDic = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    with open(jsonFile, 'w') as json_file:
        json_file.write(jsonDic)




if __name__ == "__main__":
    import time
    a = time.time()
    # read_json("test.json")
    # imgdata = read_json("testmov/test3.mov.json")
    # img_decode = numpy.fromstring(imgdata["1"], numpy.uint8)
    # frame = cv2.imdecode(img_decode, cv2.IMREAD_COLOR)
    # print frame, img_decode, frame.shape

    # write_json({1:"?郳u0000\u0010JFIF\u"}, "test.json")
    # print read_json("test.json")["1"]

    # f = open("testmov/test3.mov.json", "rb")
    # data = f.read()
    # f.close()
    # img_decode = numpy.fromstring(data, numpy.uint8)
    # # img_decode = numpy.fromfile("testmov/test3.mov.json", numpy.uint8)
    # frame = cv2.imdecode(img_decode, cv2.IMREAD_COLOR)
    # print frame, img_decode, frame.shape

    cacheFile = "test.cache"
    f = open(cacheFile, 'wb')
    for i in range(1, 20, 2):
        f.write("##########%s##########" % i)
        f.write("assda\nasasd\tfvxfv\nsdf")
    f.close()

    f = open(cacheFile, "rb")
    data = f.read()
    f.close()
    cacheFrames = {}
    frames = data.split("##########")
    print frames
    length = len(frames[1:])
    for i in range(1, length, 2):
        print frames[i]
        cacheFrames[int(frames[i])] = frames[i+1]
    print cacheFrames

    b = time.time()
    print b - a

