# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/15/2018

import os
import random
import time
import datetime
from sins.db.models import *
from sins.db.default_run import run_default
from sins.utils.encrypt import do_hash
from test_person import gen_one_gender_word

# TEST_DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'test_data')
TEST_DATA_FOLDER = os.path.abspath('../../../test/test_data')


def get_random_time(t1=(2010,1,1,0,0,0,0,0,0), t2=(2018,12,31,23,59,59,0,0,0)):
    start = time.mktime(t1)
    end = time.mktime(t2)

    t = random.randint(start, end)
    d = datetime.datetime.fromtimestamp(t)
    return d


# database.connect()

'''
'''
def drop_and_create_table():
    print '# ------------create table------------ #'
    drop_and_create(database)
    print 'create table successful'


def create_default():
    print '# ------------create default data------------ #'
    run_default()
    print 'create default data successful'


def test_person():
    print '# ------------test person data------------ #'
    person_data = []
    for i in range(200):
        sex = ['male', 'female'][random.randint(0, 1)]
        male = sex == 'male'
        first_name = gen_one_gender_word(male=male)
        last_name = gen_one_gender_word(male=male)
        active = [True, False][random.randint(0, 1)]
        email = '{}{}@xxx.com'.format(first_name.lower(), last_name.lower())
        join_date = get_random_time()
        leave_date = None
        if not active:
            leave_date = join_date + datetime.timedelta(days=365)

        department = random.randint(1, 10)
        permission_group = random.randint(1, 5)
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


def test_project():
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


def test_add_attachment_to_project():
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


def test_add_person_to_project():
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


def test_group():
    print '# ------------test group data------------ #'
    group_data = [
        {'code': 'DRM'},
        {'code': 'DRM_CMP'},
        {'code': 'DRM_LGT'},
        {'code': 'TWL_CMP'},
        {'code': 'TWL_SUP'},
    ]
    Group.insert_many(group_data).execute()
    print 'test group data successful'


def test_add_person_to_group():
    print '# ------------test add person to group------------ #'
    drm_group = Group.get(code='DRM')
    drm_project = Project.get(code='DRM')

    persons = drm_project.persons
    prefetch(persons, GroupPersonConnection, Group)
    drm_group_persons = drm_group.persons
    for person in persons:
        if person not in drm_group_persons:
            drm_group.persons.add(person)

    drm_group_persons = drm_group.persons
    prefetch(drm_group_persons, ProjectPersonConnection, Project)

    for person in drm_group_persons:
        print person.id
        for project in person.projects:
            print project.code


    drm_cmp = Group.get(code='DRM_CMP')

    persons = (Person.select(Person, Department)
               .join(Department)
               .switch(Person).join(ProjectPersonConnection).join(Project)
               .where((Department.code == 'CMP') & (Project.code == 'DRM')))

    drm_cmp_persons = drm_cmp.persons
    for person in persons:
        if person not in drm_cmp_persons:
            drm_cmp.persons.add(person)

    drm_cmp_persons = drm_cmp.persons
    prefetch(drm_cmp_persons, ProjectPersonConnection, Project, Department)

    for person in drm_cmp_persons:
        print person.id, person.department_name
        for project in person.projects:
            print project.code
    print 'test person project relationship successful'


def test_tag():
    print '# ------------test tag data------------ #'
    drm = Project.get(code='DRM')
    tag_data = [
        {'name': 'dora', 'project': drm},
        {'name': 'nobi', 'project': drm},
    ]
    Tag.insert_many(tag_data).execute()
    print 'test tag data successful'


def test_seq_assettype():
    print '# ------------test sequence, assettype data------------ #'
    for i in range(5):
        project = Project.get(id=i + 1)
        for i in range(random.randint(5, 15)):
            status = ['wts', 'wip'][random.randint(0, 1)]
            Sequence.create(**{'name': '%s_seq%s' % (project.code, i),
                               'project': project,
                               'description': 'This is a test sequence',
                               'status': status,
                               })
        assettype_data = [
            {'name': 'character', 'project': project},
            {'name': 'building', 'project': project},
            {'name': 'prop', 'project': project},
        ]
        AssetType.insert_many(assettype_data).execute()
    print 'test sequence, assettype data successful'


def test_shot():
    print '# ------------test shot data------------ #'
    shot_data = []
    for seq in Sequence.select(Sequence, Project).join(Project):
        project = seq.project
        for j in range(random.randint(10, 50)):
            description = 'this is description ' * random.randint(1, 10)
            requirement = 'requirement is here' * random.randint(1, 10)
            head_in = 1001
            tail_out = random.randint(1016, 1116)
            duration = tail_out - head_in
            cut_in = 1009
            cut_out = tail_out - 8
            cut_duration = cut_out - cut_in
            handles = '8+8'
            final_delivery = datetime.datetime.today()

            shot_data.append({
                'name': '{}_shot{}_{}'.format(project.code, seq.id, j),
                'description': description,
                'requirement': requirement,
                'head_in': head_in,
                'tail_out': tail_out,
                'duration': duration,
                'cut_in': cut_in,
                'cut_out': cut_out,
                'cut_duration': cut_duration,
                'cut_order': j + 1,
                'handles': handles,
                'final_delivery': final_delivery,
                'sequence': seq,
                'project': seq.project
            })

    Shot.insert_many(shot_data).execute()
    print 'test shot data successful'


def test_asset():
    print '# ------------test asset data------------ #'
    asset_data = []
    for assettype in AssetType.select(AssetType, Project).join(Project):
        project = assettype.project
        for j in range(random.randint(0, 5)):
            name = '%s_%s_%s' % (project.code, assettype.name, j)
            description = 'this is description ' * random.randint(1, 10)

            asset_data.append({
                'name': name,
                'description': description,
                'asset_type': assettype,
                'project': project,
            })

    Asset.insert_many(asset_data).execute()
    print 'test asset data successful'


def test_shot_asset_relationship():
    print '# ------------test shot asset relationship------------ #'
    shots = (Shot.select(Shot, Project).join(Project).where(Project.code.in_(['DRM', 'TLW'])))
    for shot in shots:
        print shot, shot.project.code
        project = shot.project
        asset_num = random.randint(1, 5)
        shot.assets.add(Asset.select().where(Asset.project == project).order_by(fn.Random()).limit(asset_num))


    prefetch(shots, ShotAssetConnection, Asset)
    for shot in shots:
        print shot.name, 'has', len(shot.assets), 'assets: '
        for asset in shot.assets:
            print asset.name
    print 'test shot asset relationship successful'


def test_task():
    print '# ------------test task data------------ #'
    current_user_object = get_current_user_object()

    shots = (Shot.select(Shot, Project).join(Project).where(Project.code.in_(['DRM', 'TLW'])))
    assets = (Asset.select(Asset, Project).join(Project).where(Project.code.in_(['DRM', 'TLW'])))
    cmp_step = PipelineStep.get(name='cmp')
    lgt_step = PipelineStep.get(name='lgt')
    mod_step = PipelineStep.get(name='mod')

    task_data = []
    for shot in shots:
        project = shot.project
        for i in range(random.randint(1, 3)):
            task_name = 'comp_%s' % i
            task_begin = get_random_time()
            task_end = get_random_time()
            task_plan = int(datetime.timedelta(days=random.randint(1, 7)).total_seconds())

            task_data.append({
                'name': task_name,
                'begin_date': task_begin,
                'end_date': task_end,
                'planned_time': task_plan,
                'shot': shot,
                'asset': None,
                'project': project,
                'step': cmp_step,
                'assigned_from': current_user_object,
            })
        for i in range(random.randint(1, 3)):
            task_name = 'light_%s' % i
            task_begin = get_random_time()
            task_end = get_random_time()
            task_plan = int(datetime.timedelta(days=random.randint(1, 3)).total_seconds())

            task_data.append({
                'name': task_name,
                'begin_date': task_begin,
                'end_date': task_end,
                'planned_time': task_plan,
                'shot': shot,
                'asset': None,
                'project': project,
                'step': lgt_step,
                'assigned_from': current_user_object,
            })
    for asset in assets:
        project = asset.project
        for i in range(random.randint(1, 3)):
            task_name = 'model_%s' % i
            task_begin = get_random_time()
            task_end = get_random_time()
            task_plan = int(datetime.timedelta(days=random.randint(1, 3)).total_seconds())

            task_data.append({
                'name': task_name,
                'begin_date': task_begin,
                'end_date': task_end,
                'planned_time': task_plan,
                'shot': None,
                'asset': asset,
                'project': project,
                'step': mod_step,
                'assigned_from': current_user_object,
            })
    # print task_data
    Task.insert_many(task_data).execute()
    print 'test task data successful'


def test_timelog():
    print '# ------------test timelog data------------ #'
    tasks = (Task.select().limit(100))
    prefetch(tasks, Shot)
    prefetch(tasks, Asset)
    prefetch(tasks, Project)

    timelog_data = []
    for task in tasks:
        shot = task.shot
        asset = task.asset
        project = task.project
        # print shot, asset, project
        # print task.shot, task.asset, task.project
        for i in range(random.randint(3, 10)):
            description = 'this is description of timelog %s' % i
            duration = int(datetime.timedelta(days=random.randint(1, 2)).total_seconds())

            timelog_data.append({
                'description': description,
                'duration': duration,
                'task': task,
                'shot': shot,
                'asset': asset,
                'project': project,
            })

    Timelog.insert_many(timelog_data).execute()
    print 'test timelog data successful'


def test_version():
    print '# ------------test version data------------ #'
    tasks = (Task.select())
    prefetch(tasks, Shot, Sequence)
    prefetch(tasks, Asset, AssetType)
    prefetch(tasks, Project)

    version_data = []
    for task in tasks:
        shot = task.shot
        seq = shot.sequence if shot is not None else None
        asset = task.asset
        asset_type = asset.asset_type if asset is not None else None
        project = task.project

        entity = shot if shot is not None else asset

        for i in range(1, random.randint(1, 10)):
            name = '{entity}_{task}_{version}'.format(entity=entity.name, task=task.name, version='v%03d' % i)
            description = 'this is description of %s' % name
            submit_type = ['Dailies', 'Publish'][random.randint(0, 1)]
            status = ['wip', 'smtr', 'smts', 'smtc', 'aprl', 'aprs', 'aprc'][random.randint(0, 6)]
            version_path = 'this should be a path of version files'
            path_to_movie = './path/to/version/version.mov'
            path_to_frame = './path/to/version/version.####.exr'

            version_data.append({
                'name': name,
                'description': description,
                'submit_type': submit_type,
                'status': status,
                'version_path': version_path,
                'path_to_movie': path_to_movie,
                'path_to_frame': path_to_frame,

                'task': task,
                'project': project,
                'shot': shot,
                'sequence': seq,
                'asset': asset,
                'asset_type': asset_type,
            })

    Version.insert_many(version_data).execute()
    print 'test version data successful'


def test_add_version_uploaded_movie():
    print '# ------------test add version uploaded_movie data------------ #'
    test_movie01 = os.path.join(TEST_DATA_FOLDER, 'version', 'version01.mp4')
    test_movie02 = os.path.join(TEST_DATA_FOLDER, 'version', 'version02.mov')
    test_movie03 = os.path.join(TEST_DATA_FOLDER, 'version', 'version03.mov')
    test_movie04 = os.path.join(TEST_DATA_FOLDER, 'version', 'version04.jpg')

    f1 = upload_file(test_movie01)
    f2 = upload_file(test_movie02)
    f3 = upload_file(test_movie03)
    f4 = upload_file(test_movie04)

    uploaded_files = [f1, f2, f3, f4]

    versions = (Version.select().order_by(fn.Random()).limit(500))

    for version in versions:
        f = uploaded_files[random.randint(0, 3)]
        version.update_field(uploaded_movie=f)

    print 'test add version uploaded_movie successful'


if __name__ == '__main__':
    print TEST_DATA_FOLDER

    drop_and_create_table()

    create_default()

    test_person()
    test_project()
    test_add_attachment_to_project()
    test_add_person_to_project()
    test_group()
    test_add_person_to_group()
    test_tag()
    test_seq_assettype()
    test_shot()
    test_asset()
    test_shot_asset_relationship()
    test_task()
    test_timelog()
    test_version()
    test_add_version_uploaded_movie()

    database.close()
    print 'test finish, close connection'

