# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 3/27/2018

import os
import imageio
import time

os.environ['IMAGEIO_FFMPEG_EXE'] = 'D:/Program Files/ffmpeg-3.4/bin/ffmpeg.exe'


reader = imageio.get_reader('test1080.mov')
print reader
fps = reader.get_meta_data()['fps']
print fps


# for i, im in enumerate(reader):
#     print i

nums = [10, 200]
for num in nums:
    a = time.time()
    image = reader.get_data(num)
    b = time.time()
    print b - a
    # print image