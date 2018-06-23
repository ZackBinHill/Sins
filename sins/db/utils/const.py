# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/17/2018

from sins.utils.const import declare_constants


database_type = declare_constants(
    postgresql='PostgreSql',
    mysql='Mysql',
)

database_port = declare_constants(
    postgresql=5432,
    mysql=3306,
)
