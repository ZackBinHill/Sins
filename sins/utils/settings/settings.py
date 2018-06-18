# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/17/2018

from os.path import dirname as opd
from os.path import join as opj
from sins.module.sqt import QSettings, to_unicode

# Global_Setting = QSettings(QSettings.IniFormat, QSettings.SystemScope, 'Sins', 'sins')
Global_Setting = QSettings(opj(opd(opd(opd(opd(__file__)))), 'sins.ini'), QSettings.IniFormat)
User_Setting = QSettings(QSettings.IniFormat, QSettings.UserScope, 'Sins', 'sins')


def setting_to_unicode(setting):
    if isinstance(setting, basestring):
        return to_unicode(setting)
    else:
        return to_unicode(setting.toString())


def setting_to_int(setting):
    if isinstance(setting, basestring):
        return int(setting)
    else:
        return setting.toInt()[0]


def convert_setting(setting, to_type='unicode'):
    if to_type == 'unicode':
        return setting_to_unicode(setting)
    elif to_type == 'int':
        return setting_to_int(setting)
