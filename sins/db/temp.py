from sins.db.models import *

query = Shot.select()

basic_filter = [
    {'join': Project, 'where': (Project.id == 1)},
    {'join': Sequence, 'where': (Sequence.id == 1)},
    {'join': None, 'where': (Shot.id == 1) | (Shot.id == 2)},
]

for each_filter in basic_filter:
    if each_filter['join'] is not None:
        query = query.switch(Shot).join(each_filter['join']).where(each_filter['where'])
    else:
        query = query.switch(Shot).where(each_filter['where'])

print query
for q in query:
    print q
