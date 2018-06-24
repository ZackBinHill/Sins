# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/24/2018


from sins.utils.python import sort_dict_list_by_key
from sins.db.utils import data_cmp


class DataItem(object):
    def __init__(self, data):
        super(DataItem, self).__init__()
        self.data = data
        self.parent_group = None


class DataGroup(object):
    def __init__(self, field_name=None, field_value=None):
        super(DataGroup, self).__init__()
        self.field_name = field_name
        self.field_value = field_value
        self.groups = []
        self.items = []
        self.grouped = False
        self.parent_group = None

    def sort_items(self, key, reverse=False):
        data_list = [i.data for i in self.items]
        data_list = sort_dict_list_by_key(data_list, key, cmp=data_cmp, reverse=reverse)
        self.items = [DataItem(data) for data in data_list]

    def group_by(self, field=None, field_name=None, reverse=False):
        if field_name is not None:
            if not self.grouped:
                self.sort_items(field_name, reverse=reverse)
                for item in self.items:
                    value = item.data[field_name]['value']
                    if field is not None and field.pre_group_func is not None:
                        value = field.pre_group_func(value)
                    self.add_item_to_group(item, field_name, value)
                self.items = []
                self.grouped = True
            else:
                for group in self.groups:
                    group.group_by(field, field_name, reverse)

    def sort_by(self, field, field_name, reverse=False):
        if field_name is not None:
            if not self.grouped:
                self.sort_items(field_name, reverse=reverse)
            else:
                for group in self.groups:
                    group.sort_by(field, field_name, reverse)

    def add_item_to_group(self, item, field_name, field_value):
        find_group = None
        for i in self.groups:
            if i.field_name == field_name and i.field_value == field_value:
                find_group = i
                break
        if find_group is None:
            find_group = DataGroup(field_name, field_value)
            self.append(find_group)
        find_group.append(item)

    def append(self, item):
        if isinstance(item, DataItem):
            self.items.append(item)
        else:
            self.groups.append(item)
        item.parent_group = self

    def children(self):
        if self.grouped:
            return self.groups
        else:
            return self.items


def get_prefetch_model(config, depth=0):
    result = []
    if depth > 0:
        for index, prefetch_config in enumerate(config.prefetch_config):
            if index == 0:
                if prefetch_config.connection_model is not None:
                    result.append(prefetch_config.connection_model)
                result.append(prefetch_config.db_model)
            else:
                if prefetch_config.connection_model is not None:
                    result.append((prefetch_config.connection_model, config.db_model))
                    result.append(prefetch_config.db_model)
                else:
                    result.append((prefetch_config.db_model, config.db_model))
            if len(prefetch_config.prefetch_config) != 0:
                result.extend(get_prefetch_model(prefetch_config, depth=depth - 1))
    return result


def get_prefetch_models(config, depth=1):
    result = []
    for prefetch_config in config.prefetch_config:
        basic_prefetch = []
        if prefetch_config.connection_model is not None:
            basic_prefetch.append(prefetch_config.connection_model)
        basic_prefetch.append(prefetch_config.db_model)
        basic_prefetch.extend(get_prefetch_model(prefetch_config, depth))
        result.append(basic_prefetch)
    return result
