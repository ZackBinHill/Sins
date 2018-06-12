# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/19/2018


import re
from sins.utils.color.const import COLOR_DICT
from sins.utils.log import get_logger


logger = get_logger(__file__)

hex6_pattern = re.compile(r'^#[a-zA-Z0-9]{6}')
hex8_pattern = re.compile(r'^#[a-zA-Z0-9]{8}')
rgbstr_match_pattern = re.compile(r'^rgb(.*)$')
rgbstr_pattern = re.compile(r'rgb((?P<color>.+))')


def is_code(color):
    if color.lower() in COLOR_DICT:
        return True
    else:
        return False


def is_hex6(color):
    if re.match(hex6_pattern, color):
        return True
    else:
        return False


def is_hex8(color):
    if re.match(hex8_pattern, color):
        return True
    else:
        return False


def is_rgbstr(color):
    if re.match(rgbstr_match_pattern, color):
        return True
    else:
        return False


def rgba_to_int10(color_rgba, max=1.0, alpha_index=3):
    """
    convert rgb color to hex
    :param color_rgba: list or tuple
    :return: int
    """
    if len(color_rgba) == 3:
        color_rgba.append(1.0 * max)

    if alpha_index == 3:
        return int('%02x%02x%02x%02x' % (int(color_rgba[0] * 255 / max),
                                         int(color_rgba[1] * 255 / max),
                                         int(color_rgba[2] * 255 / max),
                                         int(color_rgba[3] * 255 / max)), 16)
    elif alpha_index == 0:
        return int('%02x%02x%02x%02x' % (int(color_rgba[3] * 255 / max),
                                         int(color_rgba[0] * 255 / max),
                                         int(color_rgba[1] * 255 / max),
                                         int(color_rgba[2] * 255 / max)), 16)


def int10_to_rgb(color_hex, max=1.0, alpha_index=3):
    """
    convert hex to rgba
    :param color_hex: int
    :return: r, g, b, a
    """
    red = (0xFF & color_hex >> 24) / 255.0
    green = (0xFF & color_hex >> 16) / 255.0
    blue = (0xFF & color_hex >> 8) / 255.0
    alpha = (0xFF & color_hex >> 0) / 255.0

    if alpha_index == 3:
        return red * max, green * max, blue * max, alpha * max
    elif alpha_index == 0:
        return green * max, blue * max, alpha * max, red * max


def hex6_to_rgb(color_hex):
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    return r, g, b


def hex8_to_rgb(color_hex):
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    a = int(color_hex[6:8], 16)
    return r, g, b, a


def code_to_rgb(color_code):
    color_code = color_code.lower()
    if color_code not in COLOR_DICT:
        logger.error('color name not valid')
        return
    else:
        color_str = COLOR_DICT[color_code][1:]
        return hex6_to_rgb(color_str)


def rgbstr_to_rgb(color_str):
    match = re.search(rgbstr_pattern, color_str)
    if match:
        r, g, b = eval(match.group('color'))
        r = int(r)
        g = int(g)
        b = int(b)
        return r, g, b


def other_to_rgb(color):
    if is_code(color):
        return code_to_rgb(color)
    if is_hex6(color):
        return hex6_to_rgb(color)
    if is_hex8(color):
        return hex8_to_rgb(color)
    if is_rgbstr(color):
        return rgbstr_to_rgb(color.replace(" ", ""))


def get_lum(color_rgb):
    r = color_rgb[0] if color_rgb[0] <= 1 else color_rgb[0] / 255.0
    g = color_rgb[1] if color_rgb[1] <= 1 else color_rgb[1] / 255.0
    b = color_rgb[2] if color_rgb[2] <= 1 else color_rgb[2] / 255.0
    return 0.299 * r + 0.587 * g + 0.114 * b


if __name__ == "__main__":
    print rgba_to_int10([1, 1, 1])
    print rgba_to_int10([1.0, 0.3764705882352941, 0.054901960784313725, 1.0])
    print int10_to_rgb(4284485375)  # 89 179 255
    print int10_to_rgb(100)
    print get_lum([255, 255, 5])
    print code_to_rgb('darkgray')
    print is_hex6('#aaaa1A')
    print is_hex8('#aaaa1A')
    print is_rgbstr('rgb(10, 10, 10)')
    print get_lum(other_to_rgb('rgb(20, 20, 20)'))



