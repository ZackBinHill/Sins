# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 2/8/2018

import datetime
from peewee import *


database = MySQLDatabase('shots_test01', **{'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '123456'})


class ModelBase(Model):
    class Meta:
        database = database


class Person(ModelBase):
    user_login = CharField(column_name='user_login', null=False)
    user_pwd = CharField(column_name="user_pwd", null=False)
    first_name = CharField(column_name='first_name', null=True)
    last_name = CharField(column_name='last_name', null=True)
    sex = CharField(column_name='sex', null=True)
    department = CharField(column_name='department', null=True)
    email = CharField(column_name='email', null=True)
    created_date = DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = 'person'


class Project(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(column_name="description", null=True)
    persons = ManyToManyField(Person, backref="projects")

    class Meta:
        db_table = 'project'


class Sequence(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref="seqs")

    class Meta:
        db_table = 'sequence'


class Shot(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    description = TextField(column_name="description", null=True)
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref="shots")
    sequence = ForeignKeyField(column_name='seq_id', model=Sequence, field='id', backref="shots")
    status = CharField(column_name="status", default="")  #

    class Meta:
        db_table = 'shot'


class Task(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    begin_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref="tasks")
    persons = ManyToManyField(Person, backref="tasks")
    status = CharField(column_name="status", default="")  #

    class Meta:
        db_table = 'task'


class Verson(ModelBase):
    name = CharField(column_name='NAME', null=False)
    created_date = DateTimeField(default=datetime.datetime.now())
    created_person = ForeignKeyField(column_name='created_person_id', model=Person, field='id', backref="versons")
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref="versons")
    sequence = ForeignKeyField(column_name='seq_id', model=Sequence, field='id', backref="versons")
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref="versons")
    task = ForeignKeyField(column_name='task_id', model=Task, field='id', backref="versons")
    note = TextField(column_name="note", null=True)
    preview_file = CharField(column_name='preview_file', null=True)
    submit_type = CharField(column_name="submit", default="dailies") # dailies / publish
    status = CharField(column_name="status", default="sub") #

    class Meta:
        db_table = 'verson'


class Note(ModelBase):
    created_date = DateTimeField(default=datetime.datetime.now())
    created_person = ForeignKeyField(column_name='created_person_id', model=Person, field='id', backref="out_notes")
    to_person = ForeignKeyField(column_name='to_person_id', model=Person, field='id', backref="in_notes")
    project = ForeignKeyField(column_name='project_id', model=Project, field='id', backref="notes")
    shot = ForeignKeyField(column_name='shot_id', model=Shot, field='id', backref="notes")
    verson = ForeignKeyField(column_name='verson_id', model=Verson, field='id', backref="notes")
    content = TextField(column_name="content", null=True)
    attachment_path = TextField(column_name="attachment_path", null=True)

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
    database.drop_tables(tables, safe=True)

    '''
    
    database.create_tables(all_tables, safe=True)
    
    # time2 = time.time()
    
    aaa = Person.create(user_id="aaa", user_pwd="0000")
    bbb = Person.create(user_id="bbb", user_pwd="0000")
    clp = Project.create(name="CLP")
    cwt = Project.create(name="CWT")
    
    cwt.persons.add([aaa, bbb])
    clp.persons.add(aaa)
    
    seq01 = Sequence.create(name="37a", project=cwt)
    shot01 = Shot.create(name="0920", project=cwt, sequence=seq01)
    task01 = Task.create(name="lgt", shot=shot01)
    task02 = Task.create(name="cmp", shot=shot01)
    
    task01.persons.add([aaa, bbb])
    
    verson01 = Verson.create(created_person=aaa, project=cwt, sequence=seq01, shot=shot01, task=task01, name="0920_cmp_v001")
    
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
