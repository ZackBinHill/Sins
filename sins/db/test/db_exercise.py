# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/13/2018

from functools import partial
from peewee import *
import time

db = MySQLDatabase('exercises', **{'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '123456'})

class BaseModel(Model):
    class Meta:
        database = db

class Member(BaseModel):
    memid = AutoField()  # Auto-incrementing primary key.
    surname = CharField()
    firstname = CharField()
    address = CharField(max_length=300)
    zipcode = IntegerField()
    telephone = CharField()
    recommendedby = ForeignKeyField('self', backref='recommended',
                                    column_name='recommendedby', null=True)
    joindate = DateTimeField()

    class Meta:
        table_name = 'members'


# Conveniently declare decimal fields suitable for storing currency.
MoneyField = partial(DecimalField, decimal_places=2)


class Facility(BaseModel):
    facid = AutoField()
    name = CharField()
    membercost = MoneyField()
    guestcost = MoneyField()
    initialoutlay = MoneyField()
    monthlymaintenance = MoneyField()

    class Meta:
        table_name = 'facilities'


class Booking(BaseModel):
    bookid = AutoField()
    facility = ForeignKeyField(Facility, column_name='facid')
    member = ForeignKeyField(Member, column_name='memid')
    starttime = DateTimeField()
    slots = IntegerField()

    class Meta:
        table_name = 'bookings'



db.connect()

a = time.time()


query = (Member
         .select(Member.recommendedby, fn.COUNT(Member.memid).alias("count"))
         .where(Member.recommendedby.is_null(False))
         .group_by(Member.recommendedby)
         .order_by(Member.recommendedby))
print query
for q in query:
    print q.__data__, q.__dict__, q.recommendedby, q.count

query = (Booking
         .select(Booking.facid, fn.SUM(Booking.slots))
         .group_by(Booking.facid)
         .order_by(Booking.facid))
print query
for q in query:
    print q.__data__, q.__dict__


print time.time() - a

db.close()



