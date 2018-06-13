# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/15/2018

import os
import random
import time
import datetime
from sins.db.test.db_test05 import *
from sins.db import default
from sins.utils.encrypt import do_hash
from test_person import gen_one_gender_word

test_data_folder = os.path.join(os.path.dirname(__file__), 'data').replace('\\', '/')


def get_random_time(t1=(2010,1,1,0,0,0,0,0,0), t2=(2018,12,31,23,59,59,0,0,0)):
    start = time.mktime(t1)
    end = time.mktime(t2)

    t = random.randint(start, end)
    d = datetime.datetime.fromtimestamp(t)
    return d


# database.connect()

'''
'''

print '# ------------create table------------ #'
drop_and_create(database)
print 'create table successful'

print '# ------------default department data------------ #'
department_data = default.Department
for data_dict in department_data:
    Department.create(**data_dict)
print 'test department data successful'

print '# ------------default PermissionGroup data------------ #'
permissionGroup_data = default.PermissionGroup
for data_dict in permissionGroup_data:
    PermissionGroup.create(**data_dict)
print 'test PermissionGroup data successful'

print '# ------------default status data------------ #'
status_data = default.Status
for data_dict in status_data:
    Status.create(**data_dict)
print 'test status data successful'


print '# ------------default person data------------ #'
root_data = {
    'user_login': current_user,
    'user_pwd': '123456',
    'permission_group': PermissionGroup.get(name='Root')
}
Person.create(**root_data)


print '# ------------test person data------------ #'
person_data = [{
    'user_login': 'john',
    'user_pwd': do_hash(u'123456'),
    'first_name': 'Huan',
    'last_name': 'Xing',
    'full_name': 'Xing Huan',
    'cn_name': '邢欢',
    'sex': 'male',
    'email': 'aaa.com',
    'thumbnail': '%s/user.png' % test_data_folder,
    'active': True,
    'join_date': get_random_time(),
    'leave_date': None,
    'department': 1,
    'permission_group': 1,
},
]
for i in range(200):
    sex = ['male', 'female'][int(random.random() * 2)]
    department = int(random.random() * 10 + 1)
    permission_group = int(random.random() * 5 + 1)
    male = sex == 'male'
    first_name = gen_one_gender_word(male=male)
    last_name = gen_one_gender_word(male=male)
    active = [True, False][int(random.random() * 2)]
    # email = first_name.lower() + last_name.lower() + '{}{}@xxx.com'
    email = '{}{}@xxx.com'.format(first_name.lower(), last_name.lower())
    thumbnail = '%s/user.png' % test_data_folder
    join_date = get_random_time()
    leave_date = None
    if not active:
        leave_date = join_date + datetime.timedelta(days=365)

    person_data.append({
        'user_login': 'user_%s' % i,
        'user_pwd': '123456',
        'first_name': first_name,
        'last_name': last_name,
        'full_name': first_name + ' ' + last_name,
        'cn_name': first_name + ' ' + last_name,
        'sex': sex,
        'email': email,
        'thumbnail': thumbnail,
        'active': active,
        'join_date': join_date,
        'leave_date': leave_date,
        'department': department,
        'permission_group': permission_group,
    }
    )
Person.insert_many(person_data).execute()
print 'test person data successful'


print '# ------------test project data------------ #'
project_data = [
    {'name': 'DRM', 'description': 'Doraemon animation', 'thumbnail': '%s/DRM.png' % test_data_folder},
    {'name': 'XYY', 'description': '喜羊羊与灰太狼', 'thumbnail': ''},
    {'name': 'TLW', 'description': 'Tiny little life in the woods', 'thumbnail': '%s/TLW.jpg' % test_data_folder},
    {'name': 'NCJ', 'description': 'nichijyou', 'thumbnail': '%s/NCJ.jpg' % test_data_folder},
]
Project.insert_many(project_data).execute()
print 'test project data successful'


print '# ------------test add person to project------------ #'
drm = Project.get(name='DRM')
drm.persons.add(Person.select().where(Person.id < 100))
for person in drm.persons:
    print person.user_login

tlw = Project.get(name='TLW')
root = Person.get(user_login=current_user)
root.projects.add(tlw)
tlw.persons.add(Person.select().where((Person.id > 50) & (Person.id < 80)))
for person in tlw.persons:
    print person.user_login
print 'test person project relationship successful'


print '# ------------test group data------------ #'
group_data = [
    {'name': 'DRM'},
    {'name': 'DRM_CMP'},
]
Group.insert_many(group_data).execute()
print 'test group data successful'

print '# ------------test add person to group------------ #'
drm_cmp = Group.get(name='DRM_CMP')
drm_cmp.persons.add(Person.select().where((Person.id < 5)))
for person in drm_cmp.persons:
    print person.user_login
print 'test person project relationship successful'


print '# ------------default pipeline step data------------ #'
step_data = default.PipelineStep
for data_dict in step_data:
    PipelineStep.create(**data_dict)
print 'test pipeline step data successful'


print '# ------------test tag data------------ #'
drm = Project.get(name='DRM')
tag_data = [
    {'name': 'duola', 'project': drm},
    {'name': 'nuobi', 'project': drm},
]
Tag.insert_many(tag_data).execute()
print 'test tag data successful'


print '# ------------test sequence, assettype data------------ #'
for i in range(4):
    project = Project.get(id=i + 1)
    for i in range(10):
        Sequence.create(**{'name': 'seq%s' % i, 'project': project})
    assettype_data = [
        {'name': 'character', 'project': project},
        {'name': 'building', 'project': project},
        {'name': 'prop', 'project': project},
    ]
    AssetType.insert_many(assettype_data).execute()
print 'test sequence, assettype data successful'


print '# ------------test shot data------------ #'
shot_data = []
for i in range(5):
    id = int(random.random() * 40 + 1)
    seq = Sequence.get(id=id)
    for j in range(100):
        description = 'description ' * int(random.random() * 10 + 1)
        requirement = 'requirement ' * int(random.random() * 10 + 1)
        head_in = 1001
        tail_out = int(random.random() * 100 + 1001)
        duration = tail_out - head_in
        cut_in = 1009
        cut_out = tail_out - 8
        cut_duration = cut_out - cut_in
        handles = '8+8'
        final_delivery = datetime.datetime.today()
        thumbnail = '%s/shot.png' % test_data_folder
        shot_data.append({
            'name': 'shot{}_{}'.format(id, j),
            'description': description,
            'requirement': requirement,
            'head_in': head_in,
            'tail_out': tail_out,
            'duration': duration,
            'cut_in': cut_in,
            'cut_out': cut_out,
            'cut_duration': cut_duration,
            'handles': handles,
            'final_delivery': final_delivery,
            'thumbnail': thumbnail,
            'sequence': seq,
            'project': seq.project
        })

Shot.insert_many(shot_data).execute()
print 'test shot data successful'


print '# ------------test asset data------------ #'
drm_character = AssetType.get(name='character')
drm_building = AssetType.get(name='building')
asset_data = []
for i in range(5):
    asset_data.append({
        'name': 'character_%s' % i,
        'asset_type': drm_character,
        'project': drm_character.project
    })
for i in range(10):
    asset_data.append({
        'name': 'building_%s' % i,
        'asset_type': drm_building,
        'project': drm_building.project
    })

Asset.insert_many(asset_data).execute()
print 'test asset data successful'


print '# ------------test shot asset relationship------------ #'
drm = Project.get(name='DRM')
for shot in Shot.select().where(Shot.project == drm):
    asset_num = int(random.random() * 5 + 1)
    shot.assets.add(Asset.select().where(Asset.project == drm).order_by(fn.Random()).limit(asset_num))
    print shot.name, 'has', shot.assets.count(), 'assets: '
    for asset in shot.assets:
        print asset.name
print 'test shot asset relationship successful'



database.close()
print 'test finish, close connection'

