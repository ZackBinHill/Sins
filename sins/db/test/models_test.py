# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/8/2018

import os
from peewee import *
import datetime
import time
from utils.env.consts import login_env
from utils.encrypt import do_decrypt

user = os.environ.get(login_env.user)
pwd = do_decrypt(os.environ.get(login_env.pwd))
# print pwd

connect_dict = {
    'host': 'localhost',
    'port': 3306,
    'user': user,
    'password': pwd
}

database = MySQLDatabase('test_schema', **connect_dict)


def get_current_user():
    cursor = database.cursor()
    cursor.execute('select user()')
    data = cursor.fetchone()
    current_user = data[0].split('@')[0]
    return current_user


class ModelBase(Model):
    created_date = DateTimeField(column_name='created_date', default=datetime.datetime.now())
    update_date = DateTimeField(column_name='update_time',
                                constraints=[SQL('DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')])
    created_by = CharField(column_name='created_by', null=True)
    update_by = CharField(column_name='update_by', null=True)

    def save(self, *args, **kwargs):
        super(ModelBase, self).save(*args, **kwargs)

        current_user = get_current_user(database)

        module = self.__class__
        if self.created_by is None:
            query = module.update(created_by=current_user).where(module.id == self.id)
            query.execute()
        query = module.update(update_by=current_user, update_date=datetime.datetime.now()).where(module.id == self.id)
        query.execute()

    @classmethod
    def update_(cls, __data=None, **update):

        update['update_by'] = get_current_user(database)

        return cls.update(__data, **update)

    class Meta:
        database = database


class Project(ModelBase):
    name = CharField(column_name='NAME', null=False)
    description = TextField(column_name="description", null=True)
    active = BooleanField(column_name='active', default=True)

    class Meta:
        db_table = 'project'

class Sequence(ModelBase):
    name = CharField(column_name='NAME', null=False)
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref="seqs", null=True)

    class Meta:
        db_table = 'sequence'


class SequenceRelationship(ModelBase):
    from_version = ForeignKeyField(Sequence, backref='destinations')
    to_version = ForeignKeyField(Sequence, backref='sources')

    class Meta:
        indexes = ((('from_version', 'to_version'), True),)


if __name__ == "__main__":
    # database = MySQLDatabase('test_schema', **{'host': 'localhost', 'port': 3306, 'user': 'user1', 'password': '123456'})

    database.connect()

    print get_current_user()

    tables = [Project, Sequence, SequenceRelationship]
    # database.drop_tables(all_tables, safe=True)

    # database.create_tables(all_tables, safe=True)
    # clp = Project.create(name="CLP")
    # seq01 = Sequence.create(name="37a", project=clp)
    # seq02 = Sequence.create(name="37b")
    # seq03 = Sequence.create(name="37c")
    # seq04 = Sequence.create(name="37d")

    # test = Sequence.get(id=1)
    # test.name = "37a_0a"
    # test.save(only=(Sequence.name, ))

    # query = Sequence.update_(name="37a_01").where(Sequence.id == 1)
    # query.execute()

    seq01 =Sequence.get(id=1)
    seq02 =Sequence.get(id=2)
    exist = SequenceRelationship.select().where(SequenceRelationship.from_version == seq01 & SequenceRelationship.to_version == seq02)
    print exist.count()
    # SequenceRelationship.create(from_version=Sequence.get(id=2), to_version=Sequence.get(id=1))
    print seq01.sources.count(), seq01.destinations.count()


    database.close()