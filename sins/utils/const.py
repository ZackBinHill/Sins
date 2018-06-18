import collections


VIDEO_EXT = [".mp4", ".mov"]
IMG_EXT = [".bmp", ".jpeg", ".jpg", ".png", ".pbm", ".pgm", ".ppm", ".tiff", ".tif"]
THUMB_MAX_CACHE_FRAMES = 50.0
THUMB_FIXED_WIDTH = 200


def declare_constants(**name_value_dict):
    ConstantContainer = collections.namedtuple(
        'ConstantContainer',
        name_value_dict.keys()
    )
    return ConstantContainer(**name_value_dict)

