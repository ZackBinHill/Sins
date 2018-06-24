# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/21/2018

import os
import sys
from sins.module.db.peewee import *
from sins.utils.env.consts import login_env
from sins.utils.encrypt import do_decrypt
from sins.utils.log import get_logger
from sins.utils.settings import Global_Setting, global_settings, convert_setting
from sins.db.utils.const import database_type

logger = get_logger(__file__)

host_setting = Global_Setting.value(global_settings.database_host)
host = convert_setting(host_setting)

port_setting = Global_Setting.value(global_settings.database_port)
port = convert_setting(port_setting, to_type='int')

dbtype_setting = Global_Setting.value(global_settings.database_type)
dbtype = convert_setting(dbtype_setting)

db_name_setting = Global_Setting.value(global_settings.database_name)
db_name = convert_setting(db_name_setting)

data_path_setting = Global_Setting.value(global_settings.data_path)
data_path = convert_setting(data_path_setting)

user = os.environ.get(login_env.user)
pwd = os.environ.get(login_env.pwd)

# user = 'root'
user = 'postgres'
pwd = '123456'

if user is None or pwd is None:
    logger.error('Need login first')
    sys.exit()
elif os.environ.get(login_env.pwd) is not None:
    pwd = do_decrypt(pwd)

# print user
# print pwd

connect_dict = {
    'host': host,
    'port': port,
    'user': user,
    'password': pwd
}


if dbtype == database_type.postgresql:
    database = PostgresqlDatabase(db_name, **connect_dict)
elif dbtype == database_type.mysql:
    database = MySQLDatabase(db_name, **connect_dict)

if __name__ == '__main__':
    database.connect()
    database.close()
