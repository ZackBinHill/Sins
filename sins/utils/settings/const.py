# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/17/2018

from ..const import declare_constants

global_settings = declare_constants(
    database_type='Database/Type',
    database_host='Database/Host',
    database_port='Database/Port',
    database_name='Database/Name',

    data_path='Data/path',

    thumb_auto_update='Sins/thumb_auto_update',

    rv_path='App/rv_path',
)

user_settings = declare_constants(
    user_login='Database/Login',
    user_pwd='Database/Pwd',
)
