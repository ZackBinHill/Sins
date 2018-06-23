# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/23/2018

import sys

from sins.module.db.peewee import *


database = PostgresqlDatabase('deferred_test', **{
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '123456'
})



class DeferredManager(object):
    def __init__(self):
        super(DeferredManager, self).__init__()
        self.fk_model_names = []
        self.deferred_fks = []
        self.links = {}

    def fk(self, fk_model_name, *args, **kwargs):
        if fk_model_name not in self.fk_model_names:
            self.fk_model_names.append(fk_model_name)
        deferred_fk = DeferredForeignKey(fk_model_name, *args, **kwargs)
        self.deferred_fks.append(deferred_fk)
        return deferred_fk

    def mtm(self, model_name, through_model_name, *args, **kwargs):
        deferred_through_model = DeferredThroughModel()
        many_to_many = ManyToManyField(model=model_name, through_model=deferred_through_model, *args, **kwargs)
        link = {}
        link['model_name'] = model_name
        link['field'] = many_to_many
        self.links[through_model_name] = link

        return many_to_many

    def connect(self, model_dict):
        for fk_model_name in self.fk_model_names:
            DeferredForeignKey.resolve(model_dict[fk_model_name])
        for through_model_name in self.links:
            link = self.links[through_model_name]
            many_to_many = link['field']
            many_to_many.rel_model = model_dict[link['model_name']]
            many_to_many.through_model.set_model(model_dict[through_model_name])

    def create_fk(self):
        for deferred_fk in self.deferred_fks:
            model = deferred_fk.model
            fk = getattr(model, deferred_fk.name)
            model._schema.create_foreign_key(fk)


dm = DeferredManager()





















class BaseModel(Model):

    class Meta:
        database = database




class Status(BaseModel):
    code = CharField(null=True, unique=True)
    name = CharField(null=True)
    icon = CharField(null=True, column_name='icon_id')
    color = CharField(null=True, column_name='bg_color')

    class Meta:
        db_table = 'statuses'


class Department(BaseModel):
    code = CharField(null=True)
    name = TextField(null=True)
    color = TextField()
    department_type = TextField()  # Should be either 'production' or ''

    class Meta:
        db_table = 'departments'








class Person(BaseModel):
    # department = DeferredForeignKey('Department', column_name='department_id', null=True)
    department = dm.fk('Department', column_name='department_id', null=True)
    status_ = dm.fk('Status', column_name='status_id', null=True)
    email = CharField()
    firstname = CharField(null=True)
    lastname = CharField(null=True)
    login = CharField()
    name = TextField(null=True)
    status = CharField(null=True, column_name='sg_status_list')
    start = DateTimeField(column_name='sg_start')
    # groups = ManyToManyField(Group, backref="persons", through_model=GroupPersonDeferred)
    groups = dm.mtm('Group', through_model_name='GroupPersonConnections', backref="persons")

    class Meta:
        # db_table = "users"
        db_table = "human_users"



class Group(BaseModel):
    name = TextField(null=True, column_name='code')

    class Meta:
        db_table = 'groups'





class Step(BaseModel):
    name = CharField(column_name="code", null=True)
    short_name = CharField(column_name="short_name", null=True)
    color = CharField(null=True)
    entity_type = TextField(null=True)

    class Meta:
        db_table = 'steps'


class Note(BaseModel):
    user = dm.fk('Person', column_name='user_id', null=True)
    subject = TextField(null=True)
    content = TextField(null=True)
    show = dm.fk('Show', column_name='project_id')

    DEFAULT_TYPE = "Internal"

    class Meta:
        db_table = 'notes'


class Show(BaseModel):
    name = CharField(null=True)
    description = TextField(column_name="sg_description", null=True)
    type = TextField(column_name="sg_type", null=True)
    status = CharField(null=True, column_name='sg_status')

    class Meta:
        db_table = 'projects'


class Sequence(BaseModel):
    name = CharField(column_name="code", null=True)
    description = TextField(null=True)
    show = dm.fk('Show', column_name="project_id", backref='sequences')
    status = CharField(null=True, column_name='sg_status_list')

    class Meta:
        db_table = 'sequences'




class Asset(BaseModel):
    name = CharField(column_name="code", null=True)
    description = TextField(null=True)
    show = dm.fk('Show', column_name="project_id", backref="assets")
    status = CharField(null=True, column_name='sg_status_list')
    shots = dm.mtm(
        'Shot', through_model_name='AssetShotConnection', backref="assets")
    sequences = dm.mtm(
        'Sequence', backref="assets", through_model_name='AssetSequenceConnection')

    type = TextField(column_name="sg_asset_type", null=True)

    class Meta:
        db_table = 'assets'






class Shot(BaseModel):
    name = CharField(column_name="code", null=True)
    description = TextField(null=True)
    show = dm.fk('Show', backref="shots", column_name="project_id")
    status = CharField(null=True, column_name='sg_status_list')

    sequence = dm.fk('Sequence', column_name='sg_sequence_id', backref='shots', null=True)
    start_frame = IntegerField(column_name='sg_head_in', null=True)
    end_frame = IntegerField(column_name='sg_tail_out', null=True)

    cut_duration = IntegerField(column_name='sg_cut_duration', null=True)
    cut_in = IntegerField(column_name='sg_cut_in', null=True)
    cut_out = IntegerField(column_name='sg_cut_out', null=True)

    class Meta:
        db_table = 'shots'








class GroupPersonConnections(BaseModel):
    group = dm.fk('Group', column_name="group_id")
    person = dm.fk('Person', column_name="user_id")
    date_created = None

    class Meta:
        db_table = 'group_user_connections'


class AssetShotConnection(BaseModel):
    shot = dm.fk('Shot', column_name='shot_id')
    asset = dm.fk('Asset', column_name='asset_id')

    class Meta:
        db_table = 'asset_shot_connections'


class AssetSequenceConnection(BaseModel):
    sequence = dm.fk('Sequence', column_name='sequence_id')
    asset = dm.fk('Asset', column_name='asset_id')

    class Meta:
        db_table = 'asset_sequence_connections'




all_tables = [
    Status,
    Department,
    Person,
    Group,
    Step,
    Note,
    Show,
    Sequence,
    Asset,
    Shot,
    GroupPersonConnections,
    AssetSequenceConnection,
    AssetShotConnection
]






def create_model_dict(members, obj_class):
    model_dict = {}
    for name, obj in members.items():
        try:
            if issubclass(obj, obj_class):
                model_dict[name] = obj
        except TypeError:
            pass
    return model_dict



model_dict = create_model_dict(globals().copy(), BaseModel)
# for i in model_dict:
#     print i, model_dict[i]
# for i in list(DeferredForeignKey._unresolved):
#     print i

dm.connect(model_dict)





def drop_all_table(database):
    database.drop_tables(all_tables, safe=True, cascade=True)


def create_all_table(database):
    database.create_tables(all_tables, safe=True)
    dm.create_fk()




# drop_all_table(database)
# create_all_table(database)







