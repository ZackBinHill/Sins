# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.ui.widgets.data_view.cell_edit import CellLineEdit


DEFAULT_INNER_WIDGET = CellLineEdit
DEFAULT_COLUMN_WIDTH = 100


class InField(object):
    def __init__(self,
                 name='',
                 label='',
                 model_attr=None,
                 inner_widget=DEFAULT_INNER_WIDGET,
                 widget_attr_map={},
                 column_width=DEFAULT_COLUMN_WIDTH,
                 edit_permission=[],
                 filter_enable='',
                 sort_enable=True,
                 group_enable=True,
                 group_attr=None,
                 pre_group_func=None,
                 ):
        super(InField, self).__init__()

        self.name = name
        self.label = label
        self.model_attr = model_attr if model_attr is not None else name
        self.readonly = True if len(edit_permission) == 0 else False
        self.inner_widget = inner_widget
        self.widget_attr_map = widget_attr_map
        self.column_width = column_width
        self.edit_permission = edit_permission
        self.filter_enable = filter_enable
        self.group_enable = group_enable
        self.group_attr = group_attr if group_attr is not None else name
        self.pre_group_func = pre_group_func
        self.sort_enable = sort_enable
        self.sort_attr = self.group_attr

        self.parent_configs = []
        self.label_prefix = ''

    def create_widget(self, treeitem=None, column=1, parent=None):
        cellWidgetName = self.inner_widget
        cellWidget = cellWidgetName(treeitem=treeitem,
                                    column=column,
                                    model_attr=self.model_attr,
                                    column_label=self.label,
                                    parent=parent,
                                    **self.widget_attr_map)
        if not self.readonly:
            cellWidget.add_front()

        return cellWidget


class OutField(object):
    def __init__(self,
                 name=None,
                 field_label='',
                 model_attr=None,
                 config=None,
                 ):
        super(OutField, self).__init__()

        self.name = name if name is not None else config.config_name
        self.field_label = field_label
        self.model_attr = model_attr if model_attr is not None else self.name
        self.config = config
