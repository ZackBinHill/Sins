# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/16/2018

import os
from sins.db.models import *
from sins.db import default_data


def run_default():
    print '# ------------default department data------------ #'
    department_data = default_data.Department
    for data_dict in department_data:
        Department.create(**data_dict)
    print 'test department data successful'

    print '# ------------default PermissionGroup data------------ #'
    permission_group_data = default_data.PermissionGroup
    for data_dict in permission_group_data:
        PermissionGroup.create(**data_dict)
    print 'test PermissionGroup data successful'

    print '# ------------default status data------------ #'
    status_data = default_data.Status
    for data_dict in status_data:
        status = Status.create(**data_dict)
        status.upload_file(os.path.join(default_data.DEFAULT_DATA_FOLDER, 'status', '%s.png' % data_dict['name']),
                           description='status icon file',
                           field='thumbnail')
    print 'test status data successful'

    print '# ------------default api user data------------ #'
    api_tool_data = {
        'user_login': 'api_tool01',
        'user_pwd': '123456',
        'first_name': 'api',
        'last_name': '1.0',
        'full_name': 'api 1.0',
        'permission_group': PermissionGroup.get(code='Root')
    }
    api_tool01 = create_api_user(add_to_db=True, **api_tool_data)
    api_tool01.upload_file(
        os.path.join(default_data.DEFAULT_DATA_FOLDER, 'api_user', '%s.png' % api_tool_data['user_login']),
        description='api user thumbnail')

    print '# ------------default person data------------ #'
    root_data = {
        'user_login': current_user,
        'user_pwd': '',
        'permission_group': PermissionGroup.get(code='Root')
    }
    root_user = create_human_user(add_to_db=False, **root_data)
    root_user.upload_file(os.path.join(default_data.DEFAULT_DATA_FOLDER, 'human_user', 'root.png'),
                          description='root user thumbnail')

    print '# ------------default pipeline step data------------ #'
    step_data = default_data.PipelineStep
    for data_dict in step_data:
        PipelineStep.create(**data_dict)
    print 'test pipeline step data successful'



