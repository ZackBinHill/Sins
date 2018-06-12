# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/15/2018

import logging
import inspect
import functools
import time

log_level = logging.DEBUG
log_formats = [
    '%(levelname)s:%(name)s: %(asctime)s %(pathname)s[line:%(lineno)d] %(funcName)s %(message)s',
    '%(levelname)s:%(name)s: %(asctime)s %(message)s',
]
logger_list = {}

# logging.basicConfig(level=log_level)


def get_logger(name, format=0):
    global logger_list

    if name not in logger_list:
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        date_fmt = '%d %b %Y %H:%M:%S'
        str_fmt = log_formats[format]
        formatter = logging.Formatter(str_fmt, date_fmt)
        ch_handler = logging.StreamHandler()
        ch_handler.setFormatter(formatter)
        logger.addHandler(ch_handler)
        logger_list[name] = logger
    else:
        logger = logger_list[name]
    return logger


time_logger = get_logger('log_cost_time', 1)


def log_cost_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # logger = get_logger('log_cost_time', 1)
        time_logger.debug('Enter:%s %s' % (inspect.getmodule(func).__name__, func.__name__))
        start = time.time()
        u = func(*args, **kwargs)
        time_logger.debug('Leave:%s cost time: %s' % (func.__name__, time.time() - start))
        return u
    return wrapper


def get_current_function_name():
    return inspect.stack()[1][3]
