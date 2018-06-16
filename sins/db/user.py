# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/17/2018

import traceback
from sins.db.origin_db import DATABASE_NAME, MySQLDatabase, PostgresqlDatabase
from sins.utils.log import get_logger

logger = get_logger(__name__)


# add user
def add_database_user(database, user='user1', pwd='123456'):
    cursor = database.cursor()
    if isinstance(database, MySQLDatabase):
        try:
            cursor.execute('CREATE USER "{user}"@"%" IDENTIFIED BY "{pwd}"'.format(user=user, pwd=pwd))
            cursor.execute('GRANT SELECT, INSERT, UPDATE ON {database_name}.* TO "{user}"@"%"'.format(
                database_name=DATABASE_NAME, user=user)
            )
            cursor.execute('flush privileges')
        except:
            logger.warning('Can\'t create user {user}, user may exist.'.format(user=user))
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
            logger.warning('Can\'t create user {user}, user may exist.'.format(user=user))
            database.commit()
            # traceback.print_exc()


# delete user
def drop_database_user(database, user='user1'):
    cursor = database.cursor()
    if isinstance(database, MySQLDatabase):
        try:
            cursor.execute('DROP USER "{user}"@"%"'.format(user=user))
        except:
            logger.warning('Can\'t drop user {user}.'.format(user=user))
    elif isinstance(database, PostgresqlDatabase):
        try:
            cursor.execute('REVOKE SELECT,insert,update ON ALL TABLES IN SCHEMA PUBLIC FROM {user}'.format(
                user=user))
            cursor.execute('drop role {user}'.format(user=user))
            database.commit()
        except:
            logger.warning('Can\'t drop user {user}.'.format(user=user))
            database.commit()



if __name__ == '__main__':
    from sins.db.origin_db import database

    add_database_user(database)

    drop_database_user(database)

