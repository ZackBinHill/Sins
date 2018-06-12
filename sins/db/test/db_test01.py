# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/8/2018



# peewee 2.*


import datetime
from peewee import *
from playhouse.fields import ManyToManyField

database = MySQLDatabase('shots_test01', **{'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '123456'})


class BaseModel(Model):
    class Meta:
        database = database


class Person(BaseModel):
    user_id = CharField(db_column='user_id', null=False)
    user_pwd = CharField(db_column="user_pwd", null=False)
    first_name = CharField(db_column='FIRST_NAME', null=True)
    last_name = CharField(db_column='LAST_NAME', null=True)
    sex = CharField(db_column='SEX', null=True)
    department = CharField(db_column='department', null=True)
    created_date = DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'person'


class Project(BaseModel):
    name = CharField(db_column='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(db_column="description", null=True)
    persons = ManyToManyField(Person, related_name="projects")

    class Meta:
        db_table = 'project'


class Sequence(BaseModel):
    name = CharField(db_column='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    project = ForeignKeyField(db_column='project_id', rel_model=Project, to_field='id', related_name="seqs")

    class Meta:
        db_table = 'seq'


class Shot(BaseModel):
    name = CharField(db_column='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(db_column="description", null=True)
    project = ForeignKeyField(db_column='project_id', rel_model=Project, to_field='id', related_name="shots")
    seq = ForeignKeyField(db_column='seq_id', rel_model=Sequence, to_field='id', related_name="shots")
    status = CharField(db_column="status", default="")  #

    class Meta:
        db_table = 'shot'


class Task(BaseModel):
    name = CharField(db_column='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    begin_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)
    shot = ForeignKeyField(db_column='shot_id', rel_model=Shot, to_field='id', related_name="tasks")
    persons = ManyToManyField(Person, related_name="tasks")
    status = CharField(db_column="status", default="")  #

    class Meta:
        db_table = 'task'


class Verson(BaseModel):
    name = CharField(db_column='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    created_person = ForeignKeyField(db_column='created_person_id', rel_model=Person, to_field='id', related_name="versons")
    project = ForeignKeyField(db_column='project_id', rel_model=Project, to_field='id', related_name="versons")
    seq = ForeignKeyField(db_column='seq_id', rel_model=Sequence, to_field='id', related_name="versons")
    shot = ForeignKeyField(db_column='shot_id', rel_model=Shot, to_field='id', related_name="versons")
    task = ForeignKeyField(db_column='task_id', rel_model=Task, to_field='id', related_name="versons")
    note = TextField(db_column="note", null=True)
    preview_file = CharField(db_column='preview_file', null=True)
    submit_type = CharField(db_column="submit", default="dailies") # dailies / publish
    status = CharField(db_column="status", default="sub") #

    class Meta:
        db_table = 'verson'


class Note(BaseModel):
    created_date = DateTimeField(default=datetime.datetime.now())
    created_person = ForeignKeyField(db_column='created_person_id', rel_model=Person, to_field='id', related_name="out_notes")
    to_person = ForeignKeyField(db_column='to_person_id', rel_model=Person, to_field='id', related_name="in_notes")
    project = ForeignKeyField(db_column='project_id', rel_model=Project, to_field='id', related_name="notes")
    shot = ForeignKeyField(db_column='shot_id', rel_model=Shot, to_field='id', related_name="notes")
    verson = ForeignKeyField(db_column='verson_id', rel_model=Verson, to_field='id', related_name="notes")
    content = TextField(db_column="content", null=True)
    attachment_path = TextField(db_column="attachment_path", null=True)

    class Meta:
        db_table = 'note'


# relationship
PersonProject = Project.persons.get_through_model()

PersonTask = Task.persons.get_through_model()


if __name__ == "__main__":
    import time

    # time1 = time.time()
    database.connect()
    tables = [Person, Project, Sequence, Shot, Task, Verson, Note, PersonProject, PersonTask]
    # database.drop_tables(all_tables, safe=True)


    '''
    database.create_tables(all_tables, safe=True)
    
    # time2 = time.time()
    
    aaa = Person.create(user_id="aaa", user_pwd="0000")
    bbb = Person.create(user_id="bbb", user_pwd="0000")
    clp = Project.create(name="CLP")
    cwt = Project.create(name="CWT")
    
    cwt.persons.add([aaa, bbb])
    clp.persons.add(aaa)
    
    seq01 = Seq.create(name="37a", project=cwt)
    shot01 = Shot.create(name="0920", project=cwt, seq=seq01)
    task01 = Task.create(name="lgt", shot=shot01)
    task02 = Task.create(name="cmp", shot=shot01)
    
    task01.persons.add([aaa, bbb])
    
    verson01 = Verson.create(created_person=aaa, project=cwt, seq=seq01, shot=shot01, task=task01, name="0920_cmp_v001")
    
    # time3 = time.time()
    
    aaa = Person.select().where(Person.user_id == "aaa").get()
    for verson in aaa.versons:
        print verson.created_date
        print verson.task.name
        print verson.notes
    
    
    for project in aaa.projects:
        print project.name
    
    
    
    '''

    database.close()

    # time4 = time.time()
    #
    # print time2 - time1
    # print time3 - time1
    # print time4 - time1
