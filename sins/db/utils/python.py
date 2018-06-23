# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/23/2018


def data_cmp(a, b):
    # print a, b
    if a is None:
        return -1
    elif b is None:
        return 1
    elif isinstance(a, dict) and isinstance(b, dict):
        if 'value' in a:
            return data_cmp(a['value'], b['value'])
        elif 'object' in a:
            return data_cmp(a['object'].id, b['object'].id)
    else:
        if a > b:
            return 1
        elif a < b:
            return -1
        else:
            return 0

