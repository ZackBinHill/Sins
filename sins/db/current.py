# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/24/2018

from sins.db.models import Person, current_user, database


def get_current_user_instance():
    return Person.get(user_login=current_user)


def get_current_permission():
    current_permission_group = Person.get(user_login=current_user).permission_group
    permission = current_permission_group.code
    return permission


if database.table_exists(Person._meta.table):
    current_user_object = get_current_user_instance()
    current_permission = get_current_permission()

