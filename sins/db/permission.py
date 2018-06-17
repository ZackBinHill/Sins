# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/16/2018

from sins.db.models import Project, current_user, current_permission


def get_permission_projects(user):
    """
    :param user: user object
    :return: projects
    """
    if user.permission_group.code in ['Manager', 'Read-only', 'Root']:
        return Project.select()
    else:
        return user.projects


def is_editable(db_instance=None, editable_permission=list()):
    """
    check if current user has the permission to edit the field of db_instance
    :param db_instance: model instance
    :param list editable_permission:
    :return:True or False
    """
    if current_permission == 'Read-only':
        return False
    elif current_permission in ['Lead', 'Manager', 'Supervisor', 'Coordinator', 'Root']:
        return current_permission in editable_permission
    elif current_permission == 'Artist' and current_permission in editable_permission:
        if db_instance.created_by == current_user:
            return True
    return False
