# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/21/2018

import os
import sys
from sins.module.db.peewee import *
from sins.utils.env.consts import login_env
from sins.utils.encrypt import do_decrypt
from sins.utils.log import get_logger

logger = get_logger(__file__)

DATABASE_NAME = 'sins_test05'

host = 'localhost'
# port = 3306
port = 5432

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

# database = MySQLDatabase('shots_test04', **connect_dict)
database = PostgresqlDatabase(DATABASE_NAME, **connect_dict)

