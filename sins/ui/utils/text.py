# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/21/2018

from sins.module.sqt import QFontMetrics


def get_text_wh(text, font):
    fm = QFontMetrics(font)
    text_width = fm.boundingRect(text).width()
    text_height = fm.boundingRect(text).height()
    return text_width, text_height
