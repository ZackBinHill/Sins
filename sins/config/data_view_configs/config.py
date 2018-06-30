# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from .field import *
from sins.ui.widgets.data_view.cell_edit import *
from sins.module.time_utils import datetime_to_date


class ModelConfig(object):
    def __init__(self, config_name='', db_model=None, connection_model=None):
        super(ModelConfig, self).__init__()

        self.config_name = config_name
        self.db_model = db_model
        self.connection_model = connection_model
        self.prefetch_config = []
        self.add_permission = 'Root'
        self.origin_fields = [
            InField(name='id', label='Id'),
            InField(name='created_date', label='Created Date',
                    inner_widget=CellDateEdit, pre_group_func=datetime_to_date),
            InField(name='update_date', label='Update Date',
                    inner_widget=CellDateEdit, pre_group_func=datetime_to_date),
            InField(name='created_by', label='Created By'),
            InField(name='update_by', label='Update By'),
        ]
        self._in_fields = []
        self.out_fields = []
        self.default_fields = []
        self.default_filters = ''
        self.default_sort = [{'field_name': '{}>created_date'.format(self.config_name), 'reverse': False}]
        self.default_groups = []

        self.basic_view_fields = [
            'created_date',
            'update_date',
            'created_by',
            'update_by',
            'id',
        ]
        self.extra_view_fields = [
            'id',
        ]

    @property
    def in_fields(self):
        self._in_fields.sort(cmp=self.cmp)
        return self._in_fields

    def cmp(self, a, b):
        if a.label > b.label:
            return 1
        if a.label < b.label:
            return -1
        return 0

    def refine_default_fields(self):
        for index, field_name in enumerate(self.default_fields):
            if len(field_name.split('>')) == 1:
                field_name = self.config_name + '>' + field_name
                self.default_fields[index] = field_name
        # print self.default_fields

    @property
    def first_fields(self):
        field_list = []
        field_list.extend(self.origin_fields)
        field_list.extend(self._in_fields)
        field_list.sort(cmp=self.cmp)
        return field_list

    def find_out_field(self, field_name):
        for field in self.out_fields:
            if field.name == field_name:
                return field

    def find_field(self, field_name):
        split_list = field_name.split('>')
        # print split_list
        if len(split_list) == 1:
            for field in self.first_fields:
                if field.name == field_name:
                    field.parent_configs = [self.config_name]
                    return field
        elif len(split_list) == 2:
            for field in self.first_fields:
                # print field.name
                if field.name == split_list[1]:
                    field.parent_configs = [self.config_name]
                    return field
        else:
            current_config = self
            label_prefix = ''
            for config_name in split_list[1:-1]:
                out_field = current_config.find_out_field(config_name)
                current_config = out_field.config
                label_prefix += '{}>'.format(out_field.field_label)
            field = current_config.find_field(split_list[-1])
            field.parent_configs = split_list[:-1]
            field.label_prefix = label_prefix
            return field

    def update_preference(self):
        pass


class PrefetchConfig(object):
    def __init__(self, db_model=None, connection_model=None, prefetch_config=[]):
        super(PrefetchConfig, self).__init__()

        self.db_model = db_model
        self.connection_model = connection_model
        self.prefetch_config = prefetch_config

