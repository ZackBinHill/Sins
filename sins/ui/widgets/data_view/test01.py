# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/30/2018

from db.models import *
import datetime

query = Person.select().where(Person.sex == 'male')
# print query
# for i in query:
#     print i.user_login, i.department


query = Person.select().where(Person.active == False)
print query
for i in query:
    print i.user_login, i.active


query = Person.select().where(Person.created_date > datetime.date.today())
# print query
# for i in query:
#     print i.user_login, i.active


query = Person.select(Person.sex, fn.COUNT(Person.id).alias("count")).group_by(Person.sex)
print query
for i in query:
    print i.sex, i.count

sql_count = fn.COUNT(Person.id)
query = (
    Person
    .select(Person, sql_count.alias('count'))
    .group_by(Person.sex)
    .order_by(sql_count.asc())
)
for i in query:
    print i.sex, i.count


query = Person.select().join(Department).where(Department.name == 'cmp')
print query
for i in query:
    print i.user_login, i.department.name


sql_count = fn.COUNT(Person.id)
query = Person.select(Person, sql_count.alias("count")).join(Department).group_by(Department.name).order_by(sql_count.desc())
print query
for i in query:
    print i.department.name, i.count


query = Person.select().order_by(getattr(Person, 'department')).limit(10)
# query = query.select().order_by(Person.sex)
for q in query:
    # print q.__dict__
    if q.department:
        print q.department.name, q.sex, getattr(q, 'department_name')