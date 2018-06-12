# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/14/2018

import datetime
from peewee import *


database = MySQLDatabase('shots_test03', **{'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '123456'})


class ModelBase(Model):
    class Meta:
        database = database


class Department(ModelBase):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(column_name='description', null=True)

    class Meta:
        db_table = 'department'


class Status(ModelBase):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=True)
    color = IntegerField(column_name='color', null=True)
    icon = CharField(column_name='icon_path', null=True)
    referred_table = CharField(column_name='referred_table', null=True)

    class Meta:
        db_table = 'status'


class Person(ModelBase):
    user_login = CharField(column_name='user_login', null=False)
    user_pwd = CharField(column_name='user_pwd', null=False)
    first_name = CharField(column_name='first_name', null=True)
    last_name = CharField(column_name='last_name', null=True)
    cn_name = CharField(column_name='cn_name', null=True)
    sex = CharField(column_name='sex', null=True)
    email = CharField(column_name='email', null=True)
    thumbnail = CharField(column_name='thumbnail_path', null=True)
    active = BooleanField(column_name='active', default=1)
    created_date = DateTimeField(default=datetime.datetime.now())

    department = ForeignKeyField(column_name='department_id', model=Department, field='id', backref='persons',
                                 null=True)

    class Meta:
        db_table = 'person'


class Project(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    thumbnail = CharField(column_name='thumbnail_path', null=True)
    description = TextField(column_name='description', null=True)
    status = CharField(column_name='status', default='wip')
    start_time = DateField(column_name='start_time', default=datetime.date.today())
    end_time = DateField(column_name='end_time', null=True)

    persons = ManyToManyField(Person, backref='projects')

    class Meta:
        db_table = 'project'


class Sequence(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='sequences', null=False)

    class Meta:
        db_table = 'sequence'


class AssetType(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='assettypes', null=False)

    class Meta:
        db_table = 'assettype'


class Shot(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(column_name='description', null=True)
    requirement = TextField(column_name='requirement', null=True)
    status = CharField(column_name='status', default='wts')
    fps = IntegerField(column_name='fps', default=24)
    head_in = IntegerField(column_name='head_in', null=False)
    tail_out = IntegerField(column_name='tail_out', null=False)
    duration = IntegerField(column_name='duration', null=False)
    handles = CharField(column_name='handles', default='0+0')
    final_delivery = DateField(column_name='final_delivery', null=True)
    thumbnail = CharField(column_name='thumbnail_file_path', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='shots')
    sequence = ForeignKeyField(column_name='sequence_id', model=Sequence, field='id', backref='shots')

    class Meta:
        db_table = 'shot'


class Asset(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(column_name='description', null=True)
    status = CharField(column_name='status', default='wts')
    thumbnail = CharField(column_name='thumbnail_file_path', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='assets')
    assettype = ForeignKeyField(column_name='assettype_id', model=AssetType, field='id', backref='assets')
    shots = ManyToManyField(Shot, backref='assets')

    class Meta:
        db_table = 'asset'


class Task(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(column_name='description', null=True)
    begin_date = DateField(column_name='begin_date', null=True)
    end_date = DateField(column_name='end_date', null=True)
    planned_time = DateTimeField(column_name='planned_time', null=True)
    pipeline_step = CharField(column_name='pipeline_step', null=False)
    status = CharField(column_name='status', default='wip')
    thumbnail = CharField(column_name='thumbnail_file_path', null=True)

    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref='tasks', null=True)
    asset = ForeignKeyField(column_name='asset_id', model=Asset, field='id', backref='tasks', null=True)
    assigned_from = ForeignKeyField(column_name='person_id', model=Person, field='id', backref='assignment')
    assigned_to = ManyToManyField(Person, backref='tasks')

    class Meta:
        db_table = 'task'


class Playlist(ModelBase):
    name = CharField(column_name='name', null=False)
    date_time = DateTimeField(column_name='date_time', null=True)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(column_name='description', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='playlists')
    created_by = ForeignKeyField(column_name='created_by', model=Person, field='id', backref='playlists')

    class Meta:
        db_table = 'playlist'


class Verson(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(column_name='description', null=True)
    preview_file = CharField(column_name='preview_file', null=True)
    submit_type = CharField(column_name='submit_type', default='dailies') # dailies / publish
    status = CharField(column_name='status', default='wip')
    version_path = CharField(column_name='version_path', null=True)
    uploaded_movie = CharField(column_name='uploaded_movie_path', null=True)

    created_person = ForeignKeyField(column_name='created_person_id', model=Person, field='id', backref='versons')
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='versons')
    sequence = ForeignKeyField(column_name='sequence_id', model=Sequence, field='id', backref='versons', null=True)
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref='versons', null=True)
    assettype = ForeignKeyField(column_name='assettype_id', model=AssetType, field='id', backref='versons', null=True)
    asset = ForeignKeyField(column_name='asset_id', model=Asset, field='id', backref='versons', null=True)
    task = ForeignKeyField(column_name='task_id', model=Task, field='id', backref='versons')
    playlists = ManyToManyField(Playlist, backref='versons')
    # sources = ManyToManyField('self', backref='dependences')

    class Meta:
        db_table = 'verson'


class Note(ModelBase):
    created_date = DateTimeField(default=datetime.datetime.now())
    content = TextField(column_name='content', null=True)
    attachments_path = TextField(column_name='attachments_path', null=True)

    created_person = ForeignKeyField(column_name='created_person_id', model=Person, field='id', backref='out_notes')
    to_person = ForeignKeyField(column_name='to_person_id', model=Person, field='id', backref='in_notes')
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='notes')
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref='notes', null=True)
    asset = ForeignKeyField(column_name='asset_id', model=Asset, field='id', backref='notes', null=True)
    verson = ForeignKeyField(column_name='verson_id', model=Verson, field='id', backref='notes')
    task = ForeignKeyField(column_name='task_id', model=Task, field='id', backref='notes')
    to_note = ForeignKeyField('self', backref='reply')

    class Meta:
        db_table = 'note'


# relationship
PersonProject = Project.persons.get_through_model()

AssetShot = Asset.shots.get_through_model()

PersonTask = Task.assigned_to.get_through_model()

VersonPlaylist = Verson.playlists.get_through_model()


tables = [
    Department,
    Status,
    Person,
    Project,
    Sequence,
    AssetType,
    Shot,
    Asset,
    Task,
    Playlist,
    Verson,
    Note,
    PersonProject,
    AssetShot,
    PersonTask,
    VersonPlaylist
]


def drop_all_table(database):
    database.drop_tables(tables, safe=True)

def create_all_table(database):
    database.create_tables(tables, safe=True)

def drop_and_create(database):
    drop_all_table(database)
    create_all_table(database)


if __name__ == '__main__':
    import time

    # time1 = time.time()
    database.connect()

    drop_and_create(datetime)

    database.close()

    # time4 = time.time()
    #
    # print time2 - time1
    # print time3 - time1
    # print time4 - time1
