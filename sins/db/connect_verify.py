# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/21/2018

import sins.db.origin_db as origin
reload(origin)


def main():
    print 'test connect'
    origin.database.connect()
    print 'connect successful'
    origin.database.close()
