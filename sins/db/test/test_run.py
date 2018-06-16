# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/15/2018

import os
import random
import time
import datetime
# from sins.db.test.db_test05 import *
from sins.db.models import *
from sins.db.default_run import run_default
from sins.utils.encrypt import do_hash
from test_person import gen_one_gender_word

TEST_DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'test_data')


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


print '# ------------create default data------------ #'
run_default()
print 'create default data successful'


print '# ------------test person data------------ #'
person_data = []
for i in range(200):
    sex = ['male', 'female'][int(random.random() * 2)]
    male = sex == 'male'
    first_name = gen_one_gender_word(male=male)
    last_name = gen_one_gender_word(male=male)
    active = [True, False][int(random.random() * 2)]
    email = '{}{}@xxx.com'.format(first_name.lower(), last_name.lower())
    join_date = get_random_time()
    leave_date = None
    if not active:
        leave_date = join_date + datetime.timedelta(days=365)

    department = int(random.random() * 10 + 1)
    permission_group = int(random.random() * 5 + 1)
    thumbnail = None

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
user0 = Person.get(user_login='user_0')
user0.upload_file(os.path.join(TEST_DATA_FOLDER, 'human_user', 'user.png'),
                       description='test user thumbnail')
print 'test person data successful'


print '# ------------test project data------------ #'
drm_description = 'Doraemon (Japanese: ドラえもん) is a Japanese manga series ' \
                  'written and illustrated by Fujiko F. Fujio. ' \
                  'The series has also been adapted into a successful anime series and media franchise. ' \
                  'The story revolves around a robotic cat named Doraemon, ' \
                  'who travels back in time from the 22nd century ' \
                  'to aid a pre-teen boy named Nobita Nobi (野比のび太 Nobi Nobita).'
tlw_description = 'Hakumei and Mikochi (ハクメイとミコチ) is a Japanese manga series by Takuto Kashiki. ' \
                  'It has been serialized since 2011 in Enterbrain\'s seinen manga magazine Fellows!, ' \
                  'which was renamed to Harta in 2013. It has been collected in five tankōbon volumes. ' \
                  'A 12-episode anime television series adaptation by Lerche premiered on January 12, 2018. ' \
                  'An original video animation will be included on the second Blu-ray/DVD volume released on June 27.'
ncj_description = 'Nichijou (日常 Nichijō, lit. Everyday), also known as My Ordinary Life in North America, ' \
                  'is a Japanese comedy manga series written and illustrated by Keiichi Arawi (ja). ' \
                  'The manga began serialization in the December 2006 issue ' \
                  'of Kadokawa Shoten\'s manga magazine Shōnen Ace, ' \
                  'and was also serialized in Comptiq between the March 2007 and July 2008 issues.'
gdo_description = '天使学校首席の天使が地球にやってきた！　\n' \
                  '……が、地球に馴染みすぎて学校サボりまくりのネトゲ三昧、自堕落生活。' \
                  '駄天使と化したガヴリールが贈るスクールコメディ！'
xyy_description = '《喜羊羊与灰太狼》动画主要讲述在羊历3513年，青青草原上，羊羊族群已经十分兴旺发达。' \
                  '在羊羊一族里面已经有小镇，有学校，有超市，有美容院，所有羊羊族群的羊都幸福快乐地生活。'
project_datas = [
    {'code': 'DRM', 'full_name': 'Doraemon animation', 'description': drm_description},
    {'code': 'TLW', 'full_name': 'Tiny little life in the woods', 'description': tlw_description},
    {'code': 'NCJ', 'full_name': 'nichijyou', 'description': ncj_description},
    {'code': 'GDO', 'full_name': 'ガヴリールドロップアウト', 'description': gdo_description},
    {'code': 'XYY', 'full_name': '喜羊羊与灰太狼', 'description': xyy_description},
]
Project.insert_many(project_datas).execute()
print 'test project data successful'

print '# ------------test add attachments to project------------ #'
for test_project in Project.select():
    thumbnail_file = os.path.join(TEST_DATA_FOLDER, 'project', '%s.jpg' % test_project.code)
    if not os.path.exists(thumbnail_file):
        thumbnail_file = os.path.join(TEST_DATA_FOLDER, 'project', '%s.png' % test_project.code)
    if os.path.exists(thumbnail_file):
        test_project.upload_file(thumbnail_file, description='test project thumbnail')

        test_project_data_folder = os.path.join(TEST_DATA_FOLDER, 'project')
        for f in os.listdir(test_project_data_folder):
            if f.startswith('%s_attachment' % test_project.code):
                full_path = os.path.join(test_project_data_folder, f)
                test_project.upload_file(full_path, field='attachment', description='test attachment')
print 'test add attachments to project successful'


print '# ------------test add person to project------------ #'
drm = Project.get(code='DRM')
drm.persons.add(Person.select().where(Person.id < 100))
for person in drm.persons:
    print person.user_login

tlw = Project.get(code='TLW')
root = Person.get(user_login=current_user)
root.projects.add(tlw)
tlw.persons.add(Person.select().where((Person.id > 50) & (Person.id < 80)))
for person in tlw.persons:
    print person.user_login
print 'test person project relationship successful'


print '# ------------test group data------------ #'
group_data = [
    {'code': 'DRM'},
    {'code': 'DRM_CMP'},
]
Group.insert_many(group_data).execute()
print 'test group data successful'

print '# ------------test add person to group------------ #'
drm_cmp = Group.get(code='DRM_CMP')
drm_cmp.persons.add(Person.select().where((Person.id < 5)))
for person in drm_cmp.persons:
    print person.user_login
print 'test person project relationship successful'


#
# print '# ------------test tag data------------ #'
# drm = Project.get(name='DRM')
# tag_data = [
#     {'name': 'duola', 'project': drm},
#     {'name': 'nuobi', 'project': drm},
# ]
# Tag.insert_many(tag_data).execute()
# print 'test tag data successful'
#
#
# print '# ------------test sequence, assettype data------------ #'
# for i in range(4):
#     project = Project.get(id=i + 1)
#     for i in range(10):
#         Sequence.create(**{'name': 'seq%s' % i, 'project': project})
#     assettype_data = [
#         {'name': 'character', 'project': project},
#         {'name': 'building', 'project': project},
#         {'name': 'prop', 'project': project},
#     ]
#     AssetType.insert_many(assettype_data).execute()
# print 'test sequence, assettype data successful'
#
#
# print '# ------------test shot data------------ #'
# shot_data = []
# for i in range(5):
#     id = int(random.random() * 40 + 1)
#     seq = Sequence.get(id=id)
#     for j in range(100):
#         description = 'description ' * int(random.random() * 10 + 1)
#         requirement = 'requirement ' * int(random.random() * 10 + 1)
#         head_in = 1001
#         tail_out = int(random.random() * 100 + 1001)
#         duration = tail_out - head_in
#         cut_in = 1009
#         cut_out = tail_out - 8
#         cut_duration = cut_out - cut_in
#         handles = '8+8'
#         final_delivery = datetime.datetime.today()
#         thumbnail = '%s/shot.png' % test_data_folder
#         shot_data.append({
#             'name': 'shot{}_{}'.format(id, j),
#             'description': description,
#             'requirement': requirement,
#             'head_in': head_in,
#             'tail_out': tail_out,
#             'duration': duration,
#             'cut_in': cut_in,
#             'cut_out': cut_out,
#             'cut_duration': cut_duration,
#             'handles': handles,
#             'final_delivery': final_delivery,
#             'thumbnail': thumbnail,
#             'sequence': seq,
#             'project': seq.project
#         })
#
# Shot.insert_many(shot_data).execute()
# print 'test shot data successful'
#
#
# print '# ------------test asset data------------ #'
# drm_character = AssetType.get(name='character')
# drm_building = AssetType.get(name='building')
# asset_data = []
# for i in range(5):
#     asset_data.append({
#         'name': 'character_%s' % i,
#         'asset_type': drm_character,
#         'project': drm_character.project
#     })
# for i in range(10):
#     asset_data.append({
#         'name': 'building_%s' % i,
#         'asset_type': drm_building,
#         'project': drm_building.project
#     })
#
# Asset.insert_many(asset_data).execute()
# print 'test asset data successful'
#
#
# print '# ------------test shot asset relationship------------ #'
# drm = Project.get(name='DRM')
# for shot in Shot.select().where(Shot.project == drm):
#     asset_num = int(random.random() * 5 + 1)
#     shot.assets.add(Asset.select().where(Asset.project == drm).order_by(fn.Random()).limit(asset_num))
#     print shot.name, 'has', shot.assets.count(), 'assets: '
#     for asset in shot.assets:
#         print asset.name
# print 'test shot asset relationship successful'
#
#
#
# database.close()
# print 'test finish, close connection'
#
