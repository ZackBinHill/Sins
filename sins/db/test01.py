# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/6/2018

from models import *
# from test.db_test05 import *
from sins.ui.widgets.table.data_table_configs import *

import time

t = time.time()
db_model = Shot
config = ShotConfig()

query = db_model.select()


group_field_names = [
    {'field_name': 'shot>sequence>name', 'reverse': False},
    # {'field_name': 'shot>sequence>id', 'reverse': False},
    # {'field_name': 'shot>name', 'reverse': False},
]
sort_field_names = [
    {'field_name': 'shot>id', 'reverse': True},
]




all_order_field_list = group_field_names
all_order_field_list.extend(sort_field_names)

joined_model = []

for order_field in all_order_field_list:
    if 'field' not in order_field:
        order_field['field'] = config.find_field(order_field['field_name'])

    field = order_field['field']
    field_name = order_field['field_name']
    reverse = order_field['reverse']

    parent_configs = field.parent_configs

    if len(parent_configs) <= 1:
        group_attr = field.group_attr
        # print group_attr
        if isinstance(group_attr, str):
            if reverse:
                query = query.order_by_extend(getattr(db_model, group_attr).desc())
            else:
                query = query.order_by_extend(getattr(db_model, group_attr))
        elif isinstance(group_attr, list):
            for model in group_attr[:-1]:
                print model
                if model not in joined_model:
                    query = query.join(model)
                    joined_model.append(model)
                else:
                    query = query.join(model.alias())
            if reverse:
                query = query.order_by_extend(getattr(group_attr[-2], group_attr[-1]).desc())
            else:
                query = query.order_by_extend(getattr(group_attr[-2], group_attr[-1]))
    else:
        current_config = config
        query = query.switch(db_model)
        for config_name in parent_configs[1:]:
            out_field = current_config.find_out_field(config_name)
            current_config = out_field.config
            # print current_config.db_model
            # query = query.join(current_config.db_model)
            if current_config.db_model not in joined_model:
                query = query.join(current_config.db_model)
                joined_model.append(current_config.db_model)
            else:
                query = query.join(current_config.db_model.alias())
        # print current_config.db_model, field.name, field.group_attr
        if reverse:
            query = query.order_by_extend(getattr(current_config.db_model, field.group_attr).desc())
        else:
            query = query.order_by_extend(getattr(current_config.db_model, field.group_attr))
#

# query = query.order_by_extend(Shot.id)

for q in query.limit(50):
    print q.sequence.name, q.sequence.id, q.name, q.id





print time.time() - t





























