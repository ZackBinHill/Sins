# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import QDesktopWidget


def get_screen_size():
    return QDesktopWidget().screenGeometry()