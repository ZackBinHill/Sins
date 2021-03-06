# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/14/2018

import datetime
from sins.module.db.peewee import *
from sins.db.origin_db import database
from sins.utils.res import resource


def get_current_user():
    cursor = database.cursor()
    if isinstance(database, MySQLDatabase):
        cursor.execute('select user()')
    elif isinstance(database, PostgresqlDatabase):
        cursor.execute('select current_user')
    data = cursor.fetchone()
    current_user = data[0].split('@')[0]
    return current_user


current_user = get_current_user()


class LogTable(Model):
    table_name = CharField(column_name='table_name')
    event = CharField(column_name='event')
    event_date = DateTimeField(column_name='event_date')
    event_data_id = IntegerField(column_name='event_data_id')
    event_by = CharField(column_name='event_by_user')
    detail = TextField(column_name='detail', null=True)

    class Meta:
        database = database
        db_table = 'log_table'


class ModelBase(Model):
    created_date = DateTimeField(column_name='created_date', default=datetime.datetime.now())
    update_date = DateTimeField(column_name='update_time',
                                constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    created_by = CharField(column_name='created_by', null=True)
    update_by = CharField(column_name='update_by', null=True)

    # def save(self, *args, **kwargs):
    #     super(ModelBase, self).save(*args, **kwargs)
    #
    #     module = self.__class__
    #     if self.created_by is None:
    #         query = module.update(created_by=get_current_user()).where(module.id == self.id)
    #         query.execute()
    #     query = module.update(update_by=get_current_user(), update_date=datetime.datetime.now()).where(module.id == self.id)
    #     query.execute()
    #
    # @classmethod
    # def update_(cls, __data=None, **update):
    #     update['update_by'] = get_current_user()
    #
    #     return cls.update(__data, **update)
    #
    # @classmethod
    # def insert_many_(cls, rows, fields=None):
    #     for row in rows:
    #         row.update({'created_by': get_current_user(), 'update_by': get_current_user()})
    #     return cls.insert_many(rows, fields)

    class Meta:
        database = database


class Department(ModelBase):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=False)
    description = TextField(column_name='description', null=True)
    color = BigIntegerField(column_name='color', null=True)

    class Meta:
        db_table = 'departments'


class PermissionGroup(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)

    class Meta:
        db_table = 'permission_groups'


class Person(ModelBase):
    user_login = CharField(column_name='user_login', null=False)
    user_pwd = CharField(column_name='user_pwd', null=False)
    first_name = CharField(column_name='first_name', null=True)
    last_name = CharField(column_name='last_name', null=True)
    full_name = CharField(column_name='full_name', null=True)
    cn_name = CharField(column_name='cn_name', null=True)
    sex = CharField(column_name='sex', default='male')
    email = CharField(column_name='email', null=True)
    thumbnail = TextField(column_name='thumbnail_path', null=True)
    active = BooleanField(column_name='active', default=1)
    join_date = DateField(column_name='join_date', default=datetime.date.today())
    leave_date = DateField(column_name='leave_date', null=True)

    department = ForeignKeyField(column_name='department_id', model=Department, field='id', backref='persons',
                                 null=True)
    permission_group = ForeignKeyField(column_name='permission_id', model=PermissionGroup, field='id',
                                       backref='persons', null=True)

    class Meta:
        db_table = 'persons'

    @property
    def department_name(self):
        if self.department:
            return self.department.name
        return None

    @department_name.setter
    def department_name(self, value):
        self.department = Department.get(name=value)

    @property
    def permission_group_name(self):
        if self.permission_group:
            return self.permission_group.name
        return None

    @permission_group_name.setter
    def permission_group_name(self, value):
        self.permission_group = PermissionGroup.get(name=value)


class Status(ModelBase):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=True)
    description = TextField(column_name='description', null=True)
    color = BigIntegerField(column_name='color', null=True)
    icon = TextField(column_name='icon_path', null=True)
    referred_table = CharField(column_name='referred_table', null=True)

    class Meta:
        db_table = 'statuses'


ProjectPersonDeferred = DeferredThroughModel()


class Project(ModelBase):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=True)
    thumbnail = CharField(column_name='thumbnail_path', null=True)
    description = TextField(column_name='description', null=True)
    status = CharField(column_name='status', default='wip')
    start_time = DateField(column_name='start_time', default=datetime.date.today())
    end_time = DateField(column_name='end_time', null=True)

    persons = ManyToManyField(Person, backref='projects', through_model=ProjectPersonDeferred)

    class Meta:
        db_table = 'projects'




GroupPersonDeferred = DeferredThroughModel()


class Group(ModelBase):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=True)
    description = TextField(column_name='description', null=True)

    persons = ManyToManyField(Person, backref='groups', through_model=GroupPersonDeferred)

    class Meta:
        db_table = 'groups'


class PipelineStep(ModelBase):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=True)
    color = BigIntegerField(column_name='color', null=True)
    description = TextField(column_name='description', null=True)

    class Meta:
        db_table = 'pipeline_steps'


class Sequence(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    status = CharField(column_name='status', default='wts')

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='sequences', null=False)

    class Meta:
        db_table = 'sequences'

    icon = resource.get_pic('icon', 'Sequences.png')


class AssetType(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='assettypes', null=False)

    class Meta:
        db_table = 'asset_types'


class Tag(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='tags', null=False)

    class Meta:
        db_table = 'tags'


AssetTagDeferred = DeferredThroughModel()


class Asset(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    status = CharField(column_name='status', default='wts')
    thumbnail = CharField(column_name='thumbnail_file_path', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='assets')
    asset_type = ForeignKeyField(column_name='asset_type_id', model=AssetType, field='id', backref='assets')
    tags = ManyToManyField(Tag, backref='assets', through_model=AssetTagDeferred)

    class Meta:
        db_table = 'assets'

    @property
    def asset_type_object(self):
        if self.asset_type:
            return {'object': self.asset_type, 'label': self.asset_type.name}
        return None


ShotTagDeferred = DeferredThroughModel()
ShotAssetDeferred = DeferredThroughModel()


class Shot(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    requirement = TextField(column_name='requirement', null=True)
    status = CharField(column_name='status', default='wts')
    fps = IntegerField(column_name='fps', default=24)
    head_in = IntegerField(column_name='head_in', null=False)
    tail_out = IntegerField(column_name='tail_out', null=False)
    duration = IntegerField(column_name='duration', null=False)
    cut_in = IntegerField(column_name='cut_in', null=True)
    cut_out = IntegerField(column_name='cut_out', null=True)
    cut_duration = IntegerField(column_name='cut_duration', null=True)
    handles = CharField(column_name='handles', default='0+0')
    final_delivery = DateField(column_name='final_delivery', null=True)
    thumbnail = TextField(column_name='thumbnail_file_path', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='shots')
    sequence = ForeignKeyField(column_name='sequence_id', model=Sequence, field='id', backref='shots')
    assets = ManyToManyField(Asset, backref='shots', through_model=ShotAssetDeferred)
    tags = ManyToManyField(Tag, backref='shots', through_model=ShotTagDeferred)

    class Meta:
        db_table = 'shots'

    @property
    def sequence_object(self):
        if self.sequence:
            return {'object': self.sequence, 'label': self.sequence.name}
        return None


TaskAssignToDeferred = DeferredThroughModel()


class Task(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    begin_date = DateField(column_name='begin_date', null=True)
    end_date = DateField(column_name='end_date', null=True)
    planned_time = TimestampField(column_name='planned_time', null=True)
    # pipeline_step = CharField(column_name='pipeline_step', null=False)
    status = CharField(column_name='status', default='wip')
    thumbnail = TextField(column_name='thumbnail_file_path', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='shots')
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref='tasks', null=True)
    asset = ForeignKeyField(column_name='asset_id', model=Asset, field='id', backref='tasks', null=True)
    step = ForeignKeyField(column_name='step_id', model=PipelineStep, field='id', backref='tasks', null=False)
    assigned_from = ForeignKeyField(column_name='person_id', model=Person, field='id', backref='assignment', null=True)
    assigned_to = ManyToManyField(Person, backref='tasks', through_model=TaskAssignToDeferred)

    class Meta:
        db_table = 'tasks'

    @property
    def link_object(self):
        if self.asset:
            return {'object': self.asset, 'label': self.asset.name}
        if self.shot:
            return {'object': self.shot, 'label': self.shot.name}
        return None

    @property
    def step_object(self):
        if self.step:
            return {'object': self.step, 'label': self.step.name}
        return None


class Timelog(ModelBase):
    description = TextField(column_name='description', null=True)
    duration = TimeField(column_name='duration', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='timelogs')
    task = ForeignKeyField(column_name='task_id', model=Task, field='id', backref='timelogs')
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref='timelogs', null=True)
    asset = ForeignKeyField(column_name='asset_id', model=Asset, field='id', backref='timelogs', null=True)

    class Meta:
        db_table = 'timelogs'


class Playlist(ModelBase):
    name = CharField(column_name='name', null=False)
    date_time = DateTimeField(column_name='date_time', null=True)
    description = TextField(column_name='description', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='playlists')

    class Meta:
        db_table = 'playlists'


VersionPlaylistDeferred = DeferredThroughModel()


class Version(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    submit_type = CharField(column_name='submit_type', default='dailies')  # dailies / publish
    status = CharField(column_name='status', default='wip')
    version_path = TextField(column_name='version_path', null=True)
    # preview_file = CharField(column_name='preview_file', null=True)
    uploaded_movie = TextField(column_name='uploaded_movie_path', null=True)  # for internal
    path_to_movie = TextField(column_name='path_to_movie', null=True)
    path_to_frame = TextField(column_name='path_to_frame', null=True)

    # created_person = ForeignKeyField(column_name='created_person_id', model=Person, field='id', backref='versions')
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='versions')
    sequence = ForeignKeyField(column_name='sequence_id', model=Sequence, field='id', backref='versions', null=True)
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref='versions', null=True)
    asset_type = ForeignKeyField(column_name='asset_type_id', model=AssetType, field='id', backref='versions', null=True)
    asset = ForeignKeyField(column_name='asset_id', model=Asset, field='id', backref='versions', null=True)
    task = ForeignKeyField(column_name='task_id', model=Task, field='id', backref='versions')
    playlists = ManyToManyField(Playlist, backref='versions', through_model=VersionPlaylistDeferred)

    class Meta:
        db_table = 'versions'


class VersionRelationship(ModelBase):
    from_version = ForeignKeyField(Version, backref='destinations')
    to_version = ForeignKeyField(Version, backref='sources')

    class Meta:
        indexes = ((('from_version', 'to_version'), True),)


class Note(ModelBase):
    content = TextField(column_name='content', null=True)
    attachments_path = TextField(column_name='attachments_path', null=True)

    created_person = ForeignKeyField(column_name='created_person_id', model=Person, field='id', backref='out_notes')
    to_person = ForeignKeyField(column_name='to_person_id', model=Person, field='id', backref='in_notes')
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='notes')
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref='notes', null=True)
    asset = ForeignKeyField(column_name='asset_id', model=Asset, field='id', backref='notes', null=True)
    version = ForeignKeyField(column_name='version_id', model=Version, field='id', backref='notes')
    task = ForeignKeyField(column_name='task_id', model=Task, field='id', backref='notes')
    to_note = ForeignKeyField('self', backref='reply')

    class Meta:
        db_table = 'notes'


class File(ModelBase):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    full_path = TextField(column_name='full_path', null=True)

    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref='files', null=True)
    person = ForeignKeyField(column_name='person_id', model=Person, field='id', backref='files', null=True)
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref='files', null=True)
    asset = ForeignKeyField(column_name='asset_id', model=Asset, field='id', backref='files', null=True)
    version = ForeignKeyField(column_name='version_id', model=Version, field='id', backref='files', null=True)
    task = ForeignKeyField(column_name='task_id', model=Task, field='id', backref='files', null=True)
    note = ForeignKeyField(column_name='note_id', model=Note, field='id', backref='files', null=True)

    class Meta:
        db_table = 'files'


# relationship

class ProjectPersonConnection(ModelBase):
    project = ForeignKeyField(Project)
    person = ForeignKeyField(Person)

    class Meta:
        db_table = 'project_person_connection'


class GroupPersonConnection(ModelBase):
    group = ForeignKeyField(Group)
    person = ForeignKeyField(Person)

    class Meta:
        db_table = 'group_person_connection'


class AssetTagConnection(ModelBase):
    asset = ForeignKeyField(Asset)
    tag = ForeignKeyField(Tag)

    class Meta:
        db_table = 'asset_tag_connection'


class ShotTagConnection(ModelBase):
    shot = ForeignKeyField(Shot)
    tag = ForeignKeyField(Tag)

    class Meta:
        db_table = 'shot_tag_connection'


class ShotAssetConnection(ModelBase):
    shot = ForeignKeyField(Shot)
    asset = ForeignKeyField(Asset)

    class Meta:
        db_table = 'shot_asset_connection'


class TaskAssignToConnection(ModelBase):
    task = ForeignKeyField(Task)
    assign_to = ForeignKeyField(Person)

    class Meta:
        db_table = 'task_assign_to_connection'


class VersionPlaylistConnection(ModelBase):
    version = ForeignKeyField(Version)
    playlist = ForeignKeyField(Playlist)

    class Meta:
        db_table = 'version_playlist_connection'


ProjectPersonDeferred.set_model(ProjectPersonConnection)
GroupPersonDeferred.set_model(GroupPersonConnection)
AssetTagDeferred.set_model(AssetTagConnection)
ShotTagDeferred.set_model(ShotTagConnection)
ShotAssetDeferred.set_model(ShotAssetConnection)
TaskAssignToDeferred.set_model(TaskAssignToConnection)
VersionPlaylistDeferred.set_model(VersionPlaylistConnection)


normal_tables = [
    Department,
    PermissionGroup,
    Person,
    Status,
    Project,
    Group,
    PipelineStep,
    Sequence,
    AssetType,
    Tag,
    Asset,
    Shot,
    Task,
    Timelog,
    Playlist,
    Version,
    Note,
    File,
]


connection_tables = [
    ProjectPersonConnection,
    GroupPersonConnection,
    AssetTagConnection,
    ShotTagConnection,
    ShotAssetConnection,
    TaskAssignToConnection,
    VersionPlaylistConnection,
    VersionRelationship,
]


all_tables = [LogTable,]
all_tables.extend(normal_tables)
all_tables.extend(connection_tables)


def auto_update_trigger(database):
    cursor = database.cursor()
    for table in all_tables[1:]:
        cursor.execute("""
        CREATE OR REPLACE FUNCTION data_trigger_func() RETURNS TRIGGER
        LANGUAGE plpgsql
        AS
        $$
        BEGIN
            if (TG_OP = 'INSERT') then
                NEW.created_by = user;
                NEW.created_date = CURRENT_TIMESTAMP;
                NEW.update_by = user;
                NEW.update_time = CURRENT_TIMESTAMP;
                insert into log_table(
                    table_name,
                    event_data_id,
                    event,
                    event_date,
                    event_by_user)
                values (
                    TG_TABLE_NAME,
                    NEW.id,
                    TG_OP,
                    CURRENT_TIMESTAMP,
                    user);
                RETURN NEW;
            elsif (TG_OP = 'UPDATE') then
                NEW.update_by = user;
                NEW.update_time = CURRENT_TIMESTAMP;
                insert into log_table(
                    table_name,
                    event_data_id,
                    event,
                    event_date,
                    event_by_user)
                values (
                    TG_TABLE_NAME,
                    NEW.id,
                    TG_OP,
                    CURRENT_TIMESTAMP,
                    user);
                RETURN NEW;
            elsif (TG_OP = 'DELETE') then
                insert into log_table(
                    table_name,
                    event_data_id,
                    event,
                    event_date,
                    event_by_user)
                values (
                    TG_TABLE_NAME,
                    OLD.id,
                    TG_OP,
                    CURRENT_TIMESTAMP,
                    user);
                RETURN OLD;
            end if;
            RETURN null;
        END;
        $$;
        
        CREATE TRIGGER data_trigger
            BEFORE insert or update or delete
            ON %s
            FOR EACH ROW
            EXECUTE PROCEDURE data_trigger_func();
        """ % table._meta.table_name)


def drop_all_table(database):
    database.drop_tables(all_tables, safe=True)


def create_all_table(database):
    database.create_tables(all_tables, safe=True)
    auto_update_trigger(database)


def drop_and_create(database):
    drop_all_table(database)
    create_all_table(database)


if __name__ == '__main__':
    import time

    # time1 = time.time()
    # database.connect()

    drop_and_create(database)

    database.close()

    # time4 = time.time()
    #
    # print time2 - time1
    # print time3 - time1
    # print time4 - time1
