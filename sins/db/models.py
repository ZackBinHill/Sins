# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/14/2018

import os
import shutil
import datetime
from sins.module.db.peewee import *
from sins.db.origin_db import database
from sins.db.deferred_manager import DeferredManager
from sins.db.user import add_database_user, drop_database_user
from sins.utils.res import resource
from sins.utils.encrypt import do_hash
from sins.utils.path.file import get_file_size, get_file_mime
from sins.utils.python import get_class_from_name_data, create_class_dict
from sins.utils.log import get_logger


logger = get_logger(__name__)
logger.debug('load models from %s' % __file__)


DATA_PATH = 'F:/Temp/pycharm/Sins_data/sins'


def get_current_user():
    """
    :return unicode: current database user
    """
    cursor = database.cursor()
    if isinstance(database, MySQLDatabase):
        cursor.execute('select user()')
    elif isinstance(database, PostgresqlDatabase):
        cursor.execute('select current_user')
    data = cursor.fetchone()
    current_user = data[0].split('@')[0]
    return current_user


current_user = get_current_user()


dm = DeferredManager()


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

    class Meta:
        database = database

    def update_field(self, **update):
        fields = []
        for field in update:
            old_value = getattr(self, field)
            setattr(self, field, update[field])
            fields.append(getattr(self.__class__, field))
            self.log_detail(old_value=old_value, new_value=update[field], column_name=field)
        self.save(only=tuple(fields))

    def log_detail(self,
                   old_value=None,
                   new_value=None,
                   column_name=None,
                   detail=None):
        if detail is None:
            if isinstance(new_value, ModelBase):
                new_value = new_value.id
            if isinstance(old_value, ModelBase):
                old_value = old_value.id
            detail = u'update {column} from {old} to {new}'.format(column=column_name,
                                                                   old=old_value,
                                                                   new=new_value)
        LogTable.create(
            table_name=self._meta.table_name,
            event='UPDATE',
            event_date=datetime.datetime.now(),
            event_data_id=self.id,
            event_by=current_user,
            detail=detail,
        )


class File(ModelBase):
    file_name = CharField(column_name='file_name', null=False)
    file_type = CharField(column_name='mime_type', null=True)
    file_size = BigIntegerField(column_name='file_size', null=True)
    description = TextField(column_name='description', null=True)

    class Meta:
        db_table = 'files'

    @property
    def host_path(self):
        index = '%012d' % self.id
        return '{}/File/{}/{}/{}/{}'.format(DATA_PATH,
                                            index[0:4],
                                            index[4:8],
                                            index[8:12],
                                            self.file_name)


def create_thumb(file_path):
    import sins.module.cv as cv2
    from sins.utils.const import VIDEO_EXT, IMG_EXT, THUMB_MAX_CACHE_FRAMES, THUMB_FIXED_WIDTH
    from sins.utils.io.opencv import CacheThread, ReadThread

    if os.path.splitext(file_path)[1] in VIDEO_EXT:
        cap = cv2.VideoCapture(file_path)
        frame_num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = 1
        if frame_num > THUMB_MAX_CACHE_FRAMES:
            step = int(frame_num / THUMB_MAX_CACHE_FRAMES)

        thread = CacheThread(capFile=file_path,
                             cap=cap,
                             fixwidth=THUMB_FIXED_WIDTH,
                             frameIn=1,
                             frameOut=frame_num,
                             step=step,
                             tocache=True)
        thread.start_cache()
    elif os.path.splitext(file_path)[1] in IMG_EXT:
        thread = ReadThread(readFile=file_path,
                             fixwidth=THUMB_FIXED_WIDTH
                            )
        thread.start_cache()


def upload_file(file_path, description=None):
    if os.path.exists(file_path):
        f = File.create(
            file_name=os.path.basename(file_path),
            file_type=get_file_mime(file_path),
            file_size=get_file_size(file_path, get='byte'),
            description=description
        )
        target_path = f.host_path
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))
        shutil.copyfile(file_path, target_path)
        create_thumb(target_path)
        return f
    else:
        logger.warning('upload file %s not exist' % file_path)
        return None


class Entity(ModelBase):
    @property
    def label_name(self):
        return self.id

    def upload_file(self, file_path, description=None, field='thumbnail'):
        result = upload_file(file_path, description)
        if result is not None:
            if field == 'attachment':
                current_model = self.__class__.__name__
                if hasattr(self, 'attachments'):
                    self.attachments.add(result)
                else:
                    logger.warning('not supported to upload attachment to {}!'.format(current_model))
            elif hasattr(self, field):
                setattr(self, field, result)
                self.save()
            self.log_detail(
                detail='upload new {field} to {model} {name}'.format(
                    field=field,
                    model=self.__class__.__name__,
                    name=self.label_name
                )
            )
        return result


class Department(Entity):
    code = CharField(column_name='code', null=False)
    full_name = CharField(column_name='full_name', null=False)
    description = TextField(column_name='description', null=True)
    color = BigIntegerField(column_name='color', null=True)

    class Meta:
        db_table = 'departments'

    icon = resource.get_pic('icon', 'Departments.png')

    @property
    def person_objects(self):
        return {'objects': self.persons, 'object_label_attr': 'full_name'}


class PermissionGroup(Entity):
    code = CharField(column_name='code', null=False)
    description = TextField(column_name='description', null=True)

    class Meta:
        db_table = 'permission_groups'


class Status(Entity):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=True)
    description = TextField(column_name='description', null=True)
    color = BigIntegerField(column_name='color', null=True)
    referred_table = CharField(column_name='referred_table', null=True)

    thumbnail = dm.fk(fk_model_name='File', column_name='thumbnail_id', field='id',
                                null=True)

    class Meta:
        db_table = 'statuses'

    @property
    def label_name(self):
        return self.name


class ApiUser(Entity):
    user_login = CharField(column_name='user_login', null=False)
    user_pwd = CharField(column_name='user_pwd', null=False)
    first_name = CharField(column_name='first_name', null=True)
    last_name = CharField(column_name='last_name', null=True)
    full_name = CharField(column_name='full_name', null=True)

    thumbnail = dm.fk(fk_model_name='File', column_name='thumbnail_id', field='id',
                                null=True)
    permission_group = dm.fk(fk_model_name='PermissionGroup', column_name='permission_id', field='id',
                                       backref='persons', null=True)

    class Meta:
        db_table = 'api_users'

    @property
    def label_name(self):
        return self.user_login


class Person(Entity):
    user_login = CharField(column_name='user_login', null=False)
    user_pwd = CharField(column_name='user_pwd', null=False)
    first_name = CharField(column_name='first_name', null=True)
    last_name = CharField(column_name='last_name', null=True)
    full_name = CharField(column_name='full_name', null=True)
    cn_name = CharField(column_name='cn_name', null=True)
    sex = CharField(column_name='sex', default='male')
    email = CharField(column_name='email', null=True)
    active = BooleanField(column_name='active', default=1)
    join_date = DateField(column_name='join_date', default=datetime.date.today())
    leave_date = DateField(column_name='leave_date', null=True)

    thumbnail = dm.fk(fk_model_name='File', column_name='thumbnail_id', field='id',
                                 null=True)
    department = dm.fk(fk_model_name='Department', column_name='department_id', field='id', backref='persons',
                                 null=True)
    permission_group = dm.fk(fk_model_name='PermissionGroup', column_name='permission_id', field='id',
                                       backref='persons', null=True)

    class Meta:
        db_table = 'human_users'

    icon = resource.get_pic('icon', 'Persons.png')

    @property
    def department_name(self):
        if self.department:
            return self.department.code
        return None

    @department_name.setter
    def department_name(self, value):
        self.department = Department.get(code=value)

    @property
    def permission_group_name(self):
        if self.permission_group:
            return self.permission_group.code
        return None

    @permission_group_name.setter
    def permission_group_name(self, value):
        self.permission_group = PermissionGroup.get(code=value)

    @property
    def project_objects(self):
        return {'objects': self.projects, 'object_label_attr': 'code'}

    @property
    def group_objects(self):
        return {'objects': self.groups, 'object_label_attr': 'code'}

    @property
    def label_name(self):
        return self.user_login


def create_api_user(add_to_db=True, **data_dict):
    if add_to_db:
        add_database_user(database, data_dict['user_login'], data_dict['user_pwd'])
    data_dict['user_pwd'] = do_hash(data_dict['user_pwd'])
    user = ApiUser.create(**data_dict)
    return user


def create_human_user(add_to_db=True, **data_dict):
    if add_to_db:
        add_database_user(database, data_dict['user_login'], data_dict['user_pwd'])
    data_dict['user_pwd'] = do_hash(data_dict['user_pwd'])
    user = Person.create(**data_dict)
    return user


class Project(Entity):
    code = CharField(column_name='code', null=False)
    full_name = CharField(column_name='full_name', null=True)
    description = TextField(column_name='description', null=True)
    status = CharField(column_name='status', default='wip')
    start_time = DateField(column_name='start_time', default=datetime.date.today())
    end_time = DateField(column_name='end_time', null=True)

    thumbnail = dm.fk(fk_model_name='File', column_name='thumbnail_id', field='id',
                                null=True)
    persons = dm.mtm(model_name='Person', through_model_name='ProjectPersonConnection', backref='projects')
    attachments = dm.mtm(model_name='File', through_model_name='FileProjectConnection', backref='projects')

    class Meta:
        db_table = 'projects'

    @property
    def label_name(self):
        return self.code


class Note(Entity):
    subject = TextField(column_name='subject', null=True)
    content = TextField(column_name='content', null=True)

    created_person = dm.fk(fk_model_name='Person', column_name='created_person_id', field='id', backref='out_notes')
    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='notes', null=True)

    attachments = dm.mtm(model_name='File', through_model_name='FileNoteConnection', backref='notes')
    cc = dm.mtm(model_name='Person', through_model_name='NotePersonConnection', backref='notes')

    class Meta:
        db_table = 'notes'

    @property
    def label_name(self):
        return self.subject


class Group(Entity):
    code = CharField(column_name='code', null=False)
    full_name = CharField(column_name='full_name', null=True)
    description = TextField(column_name='description', null=True)

    persons = dm.mtm(model_name='Person', through_model_name='GroupPersonConnection', backref='groups')

    class Meta:
        db_table = 'groups'

    icon = resource.get_pic('icon', 'Groups.png')


class PipelineStep(Entity):
    name = CharField(column_name='name', null=False)
    full_name = CharField(column_name='full_name', null=True)
    color = BigIntegerField(column_name='color', null=True)
    description = TextField(column_name='description', null=True)

    class Meta:
        db_table = 'pipeline_steps'

    icon = resource.get_pic('icon', 'PipelineSteps.png')


class Sequence(Entity):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    status = CharField(column_name='status', default='wts')

    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='sequences', null=False)

    class Meta:
        db_table = 'sequences'

    icon = resource.get_pic('icon', 'Sequences.png')

    @property
    def children(self):
        return self.shots


class AssetType(Entity):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)

    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='assettypes', null=False)

    class Meta:
        db_table = 'asset_types'

    @property
    def children(self):
        return self.assets


class Tag(Entity):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)

    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='tags', null=False)

    class Meta:
        db_table = 'tags'


class Asset(Entity):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    status = CharField(column_name='status', default='wts')

    thumbnail = dm.fk(fk_model_name='File', column_name='thumbnail_id', field='id',
                                null=True)
    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='assets')
    asset_type = dm.fk(fk_model_name='AssetType', column_name='asset_type_id', field='id', backref='assets')

    tags = dm.mtm(model_name='Tag', through_model_name='AssetTagConnection', backref='assets')
    attachments = dm.mtm(model_name='File', through_model_name='FileAssetConnection', backref='assets')
    notes = dm.mtm(model_name='Note', through_model_name='NoteAssetConnection', backref='assets')

    class Meta:
        db_table = 'assets'

    @property
    def label_name(self):
        return self.name

    @property
    def asset_type_object(self):
        if self.asset_type:
            return {'object': self.asset_type, 'label': self.asset_type.name}
        return None


class Shot(Entity):
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
    cut_order = IntegerField(column_name='cut_order', null=True)
    handles = CharField(column_name='handles', default='0+0')
    final_delivery = DateField(column_name='final_delivery', null=True)

    thumbnail = dm.fk(fk_model_name='File', column_name='thumbnail_id', field='id',
                                null=True)
    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='shots')
    sequence = dm.fk(fk_model_name='Sequence', column_name='sequence_id', field='id', backref='shots')

    assets = dm.mtm(model_name='Asset', through_model_name='ShotAssetConnection', backref='shots')
    tags = dm.mtm(model_name='Tag', through_model_name='ShotTagConnection', backref='shots')
    attachments = dm.mtm(model_name='File', through_model_name='FileShotConnection', backref='shots')
    notes = dm.mtm(model_name='Note', through_model_name='NoteShotConnection', backref='shots')

    class Meta:
        db_table = 'shots'

    @property
    def label_name(self):
        return self.name

    @property
    def sequence_object(self):
        if self.sequence:
            return {'object': self.sequence, 'label': self.sequence.name}
        return None


class Task(Entity):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    begin_date = DateField(column_name='begin_date', null=True)
    end_date = DateField(column_name='end_date', null=True)
    planned_time = TimestampField(column_name='planned_time', null=True)
    status = CharField(column_name='status', default='wip')
    is_main = BooleanField(column_name='is_main', default=False)

    thumbnail = dm.fk(fk_model_name='File', column_name='thumbnail_id', field='id',
                                null=True)
    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='tasks')
    shot = dm.fk(fk_model_name='Shot', column_name='shot_id', field='id', backref='tasks', null=True)
    asset = dm.fk(fk_model_name='Asset', column_name='asset_id', field='id', backref='tasks', null=True)
    step = dm.fk(fk_model_name='PipelineStep', column_name='step_id', field='id', backref='tasks', null=False)
    assigned_from = dm.fk(fk_model_name='Person', column_name='person_id', field='id', backref='assignment', null=True)

    assigned_to = dm.mtm(model_name='Person', through_model_name='TaskAssignToConnection', backref='tasks')
    attachments = dm.mtm(model_name='File', through_model_name='FileTaskConnection', backref='tasks')
    notes = dm.mtm(model_name='Note', through_model_name='NoteTaskConnection', backref='tasks')

    class Meta:
        db_table = 'tasks'

    @property
    def label_name(self):
        return self.name

    @property
    def parent(self):
        if self.shot is not None:
            return self.shot
        elif self.asset is not None:
            return self.asset
        else:
            return None

    @property
    def link_object(self):
        if self.parent is not None:
            return {'object': self.parent, 'label': self.parent.name}
        return None

    @property
    def step_object(self):
        if self.step:
            return {'object': self.step, 'label': self.step.name}
        return None


class Timelog(Entity):
    description = TextField(column_name='description', null=True)
    duration = TimestampField(column_name='duration', null=True)

    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='timelogs')
    task = dm.fk(fk_model_name='Task', column_name='task_id', field='id', backref='timelogs')
    shot = dm.fk(fk_model_name='Shot', column_name='shot_id', field='id', backref='timelogs', null=True)
    asset = dm.fk(fk_model_name='Asset', column_name='asset_id', field='id', backref='timelogs', null=True)

    class Meta:
        db_table = 'timelogs'


class Playlist(Entity):
    name = CharField(column_name='name', null=False)
    date_time = DateTimeField(column_name='date_time', null=True)
    description = TextField(column_name='description', null=True)

    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='playlists')
    
    notes = dm.mtm(model_name='Note', through_model_name='NotePlaylistConnection', backref='playlists')

    class Meta:
        db_table = 'playlists'


class Version(Entity):
    name = CharField(column_name='name', null=False)
    description = TextField(column_name='description', null=True)
    submit_type = CharField(column_name='submit_type', default='Dailies')  # Dailies / Publish
    status = CharField(column_name='status', default='wip')
    version_path = TextField(column_name='version_path', null=True)
    path_to_movie = TextField(column_name='path_to_movie', null=True)
    path_to_frame = TextField(column_name='path_to_frame', null=True)

    uploaded_movie = dm.fk(fk_model_name='File', column_name='uploaded_movie_id', field='id',null=True)
    project = dm.fk(fk_model_name='Project', column_name='project_id', field='id', backref='versions')
    sequence = dm.fk(fk_model_name='Sequence', column_name='sequence_id', field='id', backref='versions', null=True)
    shot = dm.fk(fk_model_name='Shot', column_name='shot_id', field='id', backref='versions', null=True)
    asset_type = dm.fk(fk_model_name='AssetType', column_name='asset_type_id', field='id', backref='versions',null=True)
    asset = dm.fk(fk_model_name='Asset', column_name='asset_id', field='id', backref='versions', null=True)
    task = dm.fk(fk_model_name='Task', column_name='task_id', field='id', backref='versions')
    step = dm.fk(fk_model_name='PipelineStep', column_name='step_id', field='id', backref='versions')

    playlists = dm.mtm(model_name='Playlist', through_model_name='VersionPlaylistConnection', backref='versions')
    attachments = dm.mtm(model_name='File', through_model_name='FileVersionConnection', backref='versions')
    notes = dm.mtm(model_name='Note', through_model_name='NoteVersionConnection', backref='versions')

    class Meta:
        db_table = 'versions'

    @property
    def label_name(self):
        return self.name

    @property
    def thumbnail(self):
        return self.uploaded_movie

    @property
    def entity(self):
        if self.shot is not None:
            return self.shot
        else:
            return self.asset


# relationship
class VersionRelationship(ModelBase):
    from_version = dm.fk(fk_model_name='Version', backref='destinations')
    to_version = dm.fk(fk_model_name='Version', backref='sources')

    class Meta:
        indexes = ((('from_version', 'to_version'), True),)
        db_table = 'version_relationship'


class NoteRelationship(ModelBase):
    from_note = dm.fk(fk_model_name='Note', backref='replies')
    to_note = dm.fk(fk_model_name='Note', backref='sources')

    class Meta:
        indexes = ((('from_note', 'to_note'), True),)
        db_table = 'note_relationship'


# Note connection
class NotePersonConnection(ModelBase):
    person = dm.fk(fk_model_name='Person')
    note = dm.fk(fk_model_name='Note')

    class Meta:
        indexes = ((('note', 'person'), True),)
        db_table = 'note_person_connection'


class NoteAssetConnection(ModelBase):
    asset = dm.fk(fk_model_name='Asset')
    note = dm.fk(fk_model_name='Note')

    class Meta:
        indexes = ((('note', 'asset'), True),)
        db_table = 'note_asset_connection'


class NoteShotConnection(ModelBase):
    shot = dm.fk(fk_model_name='Shot')
    note = dm.fk(fk_model_name='Note')

    class Meta:
        indexes = ((('shot', 'note'), True),)
        db_table = 'note_shot_connection'


class NoteTaskConnection(ModelBase):
    task = dm.fk(fk_model_name='Task')
    note = dm.fk(fk_model_name='Note')

    class Meta:
        indexes = ((('task', 'note'), True),)
        db_table = 'note_task_connection'


class NotePlaylistConnection(ModelBase):
    playlist = dm.fk(fk_model_name='Playlist')
    note = dm.fk(fk_model_name='Note')

    class Meta:
        indexes = ((('playlist', 'note'), True),)
        db_table = 'note_playlist_connection'


class NoteVersionConnection(ModelBase):
    version = dm.fk(fk_model_name='Version')
    note = dm.fk(fk_model_name='Note')

    class Meta:
        indexes = ((('version', 'note'), True),)
        db_table = 'note_version_connection'


# File connection
class FileProjectConnection(ModelBase):
    project = dm.fk(fk_model_name='Project')
    file = dm.fk(fk_model_name='File')

    class Meta:
        indexes = ((('project', 'file'), True),)
        db_table = 'file_project_connection'


class FileAssetConnection(ModelBase):
    asset = dm.fk(fk_model_name='Asset')
    file = dm.fk(fk_model_name='File')

    class Meta:
        indexes = ((('asset', 'file'), True),)
        db_table = 'file_asset_connection'


class FileShotConnection(ModelBase):
    shot = dm.fk(fk_model_name='Shot')
    file = dm.fk(fk_model_name='File')

    class Meta:
        indexes = ((('shot', 'file'), True),)
        db_table = 'file_shot_connection'


class FileTaskConnection(ModelBase):
    task = dm.fk(fk_model_name='Task')
    file = dm.fk(fk_model_name='File')

    class Meta:
        indexes = ((('task', 'file'), True),)
        db_table = 'file_task_connection'


class FileVersionConnection(ModelBase):
    version = dm.fk(fk_model_name='Version')
    file = dm.fk(fk_model_name='File')

    class Meta:
        indexes = ((('version', 'file'), True),)
        db_table = 'file_version_connection'


class FileNoteConnection(ModelBase):
    note = dm.fk(fk_model_name='Note')
    file = dm.fk(fk_model_name='File')

    class Meta:
        indexes = ((('note', 'file'), True),)
        db_table = 'file_note_connection'


class ProjectPersonConnection(ModelBase):
    project = dm.fk(fk_model_name='Project')
    person = dm.fk(fk_model_name='Person')

    class Meta:
        indexes = ((('project', 'person'), True),)
        db_table = 'project_person_connection'


class GroupPersonConnection(ModelBase):
    group = dm.fk(fk_model_name='Group')
    person = dm.fk(fk_model_name='Person')

    class Meta:
        indexes = ((('group', 'person'), True),)
        db_table = 'group_person_connection'


class AssetTagConnection(ModelBase):
    asset = dm.fk(fk_model_name='Asset')
    tag = dm.fk(fk_model_name='Tag')

    class Meta:
        indexes = ((('asset', 'tag'), True),)
        db_table = 'asset_tag_connection'


class ShotTagConnection(ModelBase):
    shot = dm.fk(fk_model_name='Shot')
    tag = dm.fk(fk_model_name='Tag')

    class Meta:
        indexes = ((('shot', 'tag'), True),)
        db_table = 'shot_tag_connection'


class ShotAssetConnection(ModelBase):
    shot = dm.fk(fk_model_name='Shot')
    asset = dm.fk(fk_model_name='Asset')

    class Meta:
        indexes = ((('shot', 'asset'), True),)
        db_table = 'shot_asset_connection'


class TaskAssignToConnection(ModelBase):
    task = dm.fk(fk_model_name='Task')
    assign_to = dm.fk(fk_model_name='Person')

    class Meta:
        indexes = ((('task', 'assign_to'), True),)
        db_table = 'task_assign_to_connection'


class VersionPlaylistConnection(ModelBase):
    version = dm.fk(fk_model_name='Version')
    playlist = dm.fk(fk_model_name='Playlist')

    class Meta:
        indexes = ((('version', 'playlist'), True),)
        db_table = 'version_playlist_connection'


normal_tables = [
    File,
    Department,
    PermissionGroup,
    ApiUser,
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

]

connection_tables = [
    FileProjectConnection,
    FileAssetConnection,
    FileShotConnection,
    FileTaskConnection,
    FileVersionConnection,
    FileNoteConnection,

    NotePersonConnection,
    NoteAssetConnection,
    NoteShotConnection,
    NoteTaskConnection,
    NotePlaylistConnection,
    NoteVersionConnection,

    ProjectPersonConnection,
    GroupPersonConnection,
    AssetTagConnection,
    ShotTagConnection,
    ShotAssetConnection,
    TaskAssignToConnection,
    VersionPlaylistConnection,

    VersionRelationship,
    NoteRelationship,
]

all_tables = [LogTable, ]
all_tables.extend(normal_tables)
all_tables.extend(connection_tables)


model_dict = create_class_dict(globals().copy(), ModelBase)
# for i in model_dict:
#     print i, model_dict[i]
# for i in list(DeferredForeignKey._unresolved):
#     print i
dm.connect(model_dict)



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
        """ % table._meta.table.__name__)


def drop_all_table(database):
    database.drop_tables(all_tables, safe=True, cascade=True)


def create_all_table(database):
    database.create_tables(all_tables, safe=True)
    dm.create_fk()
    auto_update_trigger(database)


def drop_and_create(database):
    drop_all_table(database)
    create_all_table(database)


def get_current_user_object():
    return Person.get(user_login=current_user)


def get_current_permission():
    current_permission_group = Person.get(user_login=current_user).permission_group
    current_permission = current_permission_group.code
    return current_permission


if database.table_exists(Person._meta.table):
    try:
        current_user_object = get_current_user_object()
        current_permission = get_current_permission()
    except:
        pass


if __name__ == '__main__':
    import time

    # time1 = time.time()
    # database.connect()

    # drop_and_create(database)
    drop_all_table(database)

    database.close()

    # time4 = time.time()
    #
    # print time2 - time1
    # print time3 - time1
    # print time4 - time1
