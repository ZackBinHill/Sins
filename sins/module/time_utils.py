# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 5/12/2018

import time
import datetime


def current_time():
    return time.time()


def now():
    return datetime.datetime.now()


def today():
    return datetime.date.today()


def str_to_datetime(string, format='%Y-%m-%d'):
    return datetime.datetime.strptime(string, format)


def datetime_to_str(date, format='%Y-%m-%d'):
    return datetime.datetime.strftime(date, format)


def datetime_to_date(t):
    # return t.month
    return t.date()


