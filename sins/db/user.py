# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/17/2018

# from sins.module.db import mysql
from sins.db.origin_db import database, DATABASE_NAME, MySQLDatabase, PostgresqlDatabase
import traceback


cursor = database.cursor()

# add user
def add_user(user='user1', pwd='123456'):
    if isinstance(database, MySQLDatabase):
        try:
            cursor.execute('CREATE USER "{user}"@"%" IDENTIFIED BY "{pwd}"'.format(user=user, pwd=pwd))
            cursor.execute('GRANT SELECT, INSERT, UPDATE ON {database_name}.* TO "{user}"@"%"'.format(
                database_name=DATABASE_NAME, user=user)
            )
            cursor.execute('flush privileges')
        except:
            print 'Can\'t create user {user}, user may exist.'.format(user=user)
            # traceback.print_exc()
    elif isinstance(database, PostgresqlDatabase):
        try:
            cursor.execute("CREATE ROLE {user} login PASSWORD '{pwd}'".format(user=user, pwd=pwd))
            cursor.execute('GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA PUBLIC TO {user}'.format(
                user=user)
            )
            database.commit()

            # -------------view user------------- #
            # select * from pg_roles;
            # -------------view permission------------- #
            # select * from pg_class where relname='departments';
        except:
            print 'Can\'t create user {user}, user may exist.'.format(user=user)
            database.commit()
            # traceback.print_exc()

add_user()

# cursor.execute('select user')
# data = cursor.fetchone()
# print data

# delete user
def delete_user(user='user1'):
    if isinstance(database, MySQLDatabase):
        try:
            cursor.execute('DROP USER "{user}"@"%"'.format(user=user))
        except:
            print 'Can\'t drop user {user}.'.format(user=user)
    elif isinstance(database, PostgresqlDatabase):
        try:
            cursor.execute('REVOKE SELECT,insert,update ON ALL TABLES IN SCHEMA PUBLIC FROM {user}'.format(
                user=user))
            cursor.execute('drop role {user}'.format(user=user))
            database.commit()
        except:
            print 'Can\'t drop user {user}.'.format(user=user)
            database.commit()

delete_user()

database.close()

