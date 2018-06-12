from sins.module.db.peewee import *


connect_dict = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '123456'
}


database = PostgresqlDatabase('test05', **connect_dict)


class ModelBase(Model):
    class Meta:
        database = database


class Status(ModelBase):
    name = CharField()

class Project(ModelBase):
    name = CharField()
    status = ForeignKeyField(Status)

class Shot(ModelBase):
    name = CharField()
    project = ForeignKeyField(Project)
    status = ForeignKeyField(Status)


all_tables = [Status, Project, Shot]


def drop_all_table(database):
    database.drop_tables(all_tables, safe=True)

def create_all_table(database):
    database.create_tables(all_tables, safe=True)

def drop_and_create(database):
    drop_all_table(database)
    create_all_table(database)

# drop_all_table(database)
# drop_and_create(database)

def test_data():
    status_data = [
        {'name': 'status01'},
        {'name': 'status02'},
        {'name': 'status03'},
        {'name': 'status04'},
    ]
    Status.insert_many(status_data).execute()

    project_data = [
        {'name': 'project01', 'status': 1},
        {'name': 'project02', 'status': 2},
        {'name': 'project03', 'status': 3},
        {'name': 'project04', 'status': 4},
    ]
    Project.insert_many(project_data).execute()

    shot_data = [
        {'name': 'shot01', 'project': 1, 'status': 1},
        {'name': 'shot02', 'project': 2, 'status': 2},
        {'name': 'shot03', 'project': 3, 'status': 3},
        {'name': 'shot04', 'project': 1, 'status': 4},
        {'name': 'shot01', 'project': 2, 'status': 1},
        {'name': 'shot02', 'project': 3, 'status': 2},
        {'name': 'shot03', 'project': 4, 'status': 3},
        {'name': 'shot04', 'project': 2, 'status': 4},
        {'name': 'shot01', 'project': 3, 'status': 1},
        {'name': 'shot02', 'project': 1, 'status': 2},
        {'name': 'shot03', 'project': 2, 'status': 3},
        {'name': 'shot04', 'project': 3, 'status': 4},
        {'name': 'shot01', 'project': 4, 'status': 1},
        {'name': 'shot02', 'project': 1, 'status': 2},
        {'name': 'shot03', 'project': 2, 'status': 3},
        {'name': 'shot04', 'project': 3, 'status': 4},
    ]
    Shot.insert_many(shot_data).execute()




query = Shot.select()
query = query.join(Status)
query = query.switch(Shot).join(Project).join(Status)

for q in query:
    print q.id




query = Shot.select()
query = query.join(Status)
query = query.order_by(Status.name)
# query = query.switch(Shot).join(Status)
# query = query.order_by(Status.name)
# query = query.switch(Shot).join(Project).join(Status)
# query = query.switch(Shot).join(Status)
# query = query.join(Project).join(Status)
# query = query.order_by(Status.name, Status.name, Shot.id)
# query = query.order_by(Status.name)
query = query.switch(Shot).join(Project)
# query = query.switch(Shot)
query = query.order_by_extend(Project.name)
query = query.order_by_extend(Shot.id)

prefetch(query, Status)
prefetch(query, Project)

for q in query:
    print q.status.name, q.project.name, q.id


