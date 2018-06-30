# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018


from sins.config.data_view_configs import *
from sins.ui.widgets.action import SeparatorAction
from .const import FOREIGN_POPULATE_DEPTH
import copy


class FieldAction(QAction):
    def __init__(self, field, enabled=True, parent=None):
        super(FieldAction, self).__init__(parent)

        self.field = field
        self.field_name = field.name

        self.setCheckable(True)

        self.setText(field.label)
        # self.setEnabled(True if field.group_enable else False)
        self.setEnabled(enabled)

    def set_parent_name(self, parent_name):
        self.field_name = '{}>{}'.format(parent_name, self.field.name)
        # self.setText(self.field_name)



class _BaseMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super(_BaseMenu, self).__init__(*args, **kwargs)

        self.menu_type = None

        self.allFieldActions = []
        self.selectedFieldNames = []
        self.config_name = ''

        self.enable_attr = None
        self.default_fields_attr = None

        self.setStyleSheet(resource.get_style('pagemenu'))

    def add_pre_actions(self):
        pass

    def add_ascend_descend(self):
        self.ascend_action = QAction('Ascend', self)
        self.descend_action = QAction('Descend', self)
        self.ascend_action.setCheckable(True)
        self.descend_action.setCheckable(True)
        if len(self.selectedFieldNames) > 0:
            sort_reverse = self.selectedFieldNames[0]['reverse']
            if sort_reverse:
                self.descend_action.setChecked(True)
            else:
                self.ascend_action.setChecked(True)
        self.addAction(self.ascend_action)
        self.addAction(self.descend_action)
        self.addSeparator()

        self.ascend_action.triggered.connect(self.ascend_triggered)
        self.descend_action.triggered.connect(self.descend_triggered)

    def check_action(self, action, check=True):
        action.toggled.disconnect(self.action_toggled)
        action.setChecked(check)
        action.toggled.connect(self.action_toggled)

    def check_ascend(self, check=True):
        if self.ascend_action.isChecked() != check:
            self.ascend_action.triggered.disconnect(self.ascend_triggered)
            self.ascend_action.setChecked(check)
            self.ascend_action.triggered.connect(self.ascend_triggered)

    def check_descend(self, check=True):
        if self.descend_action.isChecked() != check:
            self.descend_action.triggered.disconnect(self.descend_triggered)
            self.descend_action.setChecked(check)
            self.descend_action.triggered.connect(self.descend_triggered)

    def keys_of_list(self, list):
        return list

    def load_config(self, config, populate_depth=FOREIGN_POPULATE_DEPTH, first=True):
        self.selectedFieldNames = copy.deepcopy(getattr(config, self.default_fields_attr))
        # print self.default_fields_attr, self.selectedFieldNames

        self.config_name = config.config_name if first else '{}>{}'.format(self.parent().config_name,
                                                                           config.config_name)
        self.clear()
        self.allFieldActions = []
        if first:
            self.add_pre_actions()
        for in_field in config.in_fields:
            enabled = getattr(in_field, self.enable_attr) if self.enable_attr is not None else True
            action = FieldAction(in_field, enabled=enabled, parent=self)
            action.set_parent_name(self.config_name)
            self.addAction(action)
            self.allFieldActions.append(action)
        self.addSeparator()
        origin_separator = SeparatorAction('Origin Fields', self)
        self.addAction(origin_separator)
        for origin_field in config.origin_fields:
            enabled = getattr(origin_field, self.enable_attr) if self.enable_attr is not None else True
            action = FieldAction(origin_field, enabled=enabled, parent=self)
            action.set_parent_name(self.config_name)
            self.addAction(action)
            self.allFieldActions.append(action)
        if populate_depth > 0 and len(config.out_fields) > 0:
            self.addSeparator()
            out_separator = SeparatorAction('Foreign Fields', self)
            self.addAction(out_separator)
            for out_field in config.out_fields:
                # print out_field.config.in_fields
                # out_field_menu = GroupMenu(out_field.field_label, self)
                out_field_menu = _BaseMenu.create_menu(self.menu_type, out_field.field_label, self)
                out_field_menu.setObjectName('separator')
                out_field_actions = out_field_menu.load_config(out_field.config,
                                                               populate_depth=populate_depth - 1,
                                                               first=False)
                self.addMenu(out_field_menu)
                self.allFieldActions.extend(out_field_actions)
        if first:
            # print self.selectedFieldNames
            for action in self.allFieldActions:
                # print action.field_name,
                if action.field_name in self.keys_of_list(self.selectedFieldNames):
                    action.setChecked(True)
                action.toggled.connect(self.action_toggled)

        # print 'load_config:', self.__class__.__name__, self.selectedFieldNames

        return self.allFieldActions

    def action_toggled(self, checked):
        print self.sender().field_name, checked

    def ascend_triggered(self, checked):
        pass

    def descend_triggered(self, checked):
        pass

    @classmethod
    def create_menu(cls, menu_type, *args, **kwargs):
        if menu_type == 'Field':
            return FieldsMenu(*args, **kwargs)
        elif menu_type == 'Group':
            return GroupMenu(*args, **kwargs)
        elif menu_type == 'Sort':
            return SortMenu(*args, **kwargs)


class FieldsMenu(_BaseMenu):
    actionChanged = Signal(str, bool)
    def __init__(self, *args, **kwargs):
        super(FieldsMenu, self).__init__(*args, **kwargs)

        self.menu_type = 'Field'

        self.enable_attr = None
        self.default_fields_attr = 'default_fields'

    def action_toggled(self, checked):
        if checked:
            self.selectedFieldNames.append(self.sender().field_name)
            self.actionChanged.emit(self.sender().field_name, True)
        else:
            self.selectedFieldNames.remove(self.sender().field_name)
            self.actionChanged.emit(self.sender().field_name, False)


class GroupMenu(_BaseMenu):
    actionChanged = Signal(list)
    def __init__(self, *args, **kwargs):
        super(GroupMenu, self).__init__(*args, **kwargs)

        self.menu_type = 'Group'

        self.enable_attr = 'group_enable'
        self.default_fields_attr = 'default_groups'

    def keys_of_list(self, list):
        return [d['field_name'] for d in list]

    def add_pre_actions(self):
        self.ungroup_action = QAction('UnGroup', self)
        self.advanced_group_action = QAction('Advanced Group', self)
        self.addAction(self.ungroup_action)
        self.addAction(self.advanced_group_action)
        self.addSeparator()
        self.add_ascend_descend()

        self.ungroup_action.triggered.connect(self.ungroup_triggered)
        self.advanced_group_action.triggered.connect(self.advanced_group_triggered)

    def append_field(self, field, field_name, reverse=False):
        if len(self.selectedFieldNames) > 0:
            pass
        else:
            self.check_ascend(not reverse)
            self.check_descend(reverse)
        self.selectedFieldNames.append({'field':field,
                                        'field_name':field_name,
                                        'reverse':reverse})

    def remove_field(self, field_name):
        for i in self.selectedFieldNames:
            if i['field_name'] == field_name:
                self.selectedFieldNames.remove(i)
        if len(self.selectedFieldNames) > 0:
            reverse = self.selectedFieldNames[0]['reverse']
            if reverse:
                self.check_descend()
                self.check_ascend(False)
            else:
                self.check_ascend()
                self.check_descend(False)
        else:
            self.check_ascend(False)
            self.check_descend(False)

    def action_toggled(self, checked):
        if checked:
            self.append_field(self.sender().field, self.sender().field_name)
        else:
            self.remove_field(self.sender().field_name)
        # print self.selectedFieldNames
        self.actionChanged.emit(self.selectedFieldNames)

    def ungroup_triggered(self):
        if self.selectedFieldNames != []:
            self.selectedFieldNames = []
            for action in self.allFieldActions:
                if action.isChecked():
                    self.check_action(action, False)

            self.check_ascend(False)
            self.check_descend(False)

            self.actionChanged.emit(self.selectedFieldNames)

    def advanced_group_triggered(self):
        pass

    def ascend_triggered(self, checked):
        if len(self.selectedFieldNames) != 0:
            if checked:
                self.selectedFieldNames[0].update({'reverse':False})
                self.actionChanged.emit(self.selectedFieldNames)
                self.check_descend(False)
            else:
                self.check_ascend()
        else:
            self.check_ascend(not checked)

    def descend_triggered(self, checked):
        if len(self.selectedFieldNames) != 0:
            if checked:
                self.selectedFieldNames[0].update({'reverse':True})
                self.actionChanged.emit(self.selectedFieldNames)
                self.check_ascend(False)
            else:
                self.check_descend()
        else:
            self.check_descend(not checked)


class SortMenu(_BaseMenu):
    actionChanged = Signal(list)

    def __init__(self, *args, **kwargs):
        super(SortMenu, self).__init__(*args, **kwargs)

        self.menu_type = 'Sort'

        self.enable_attr = 'sort_enable'
        self.default_fields_attr = 'default_sort'
        self.reverse = False

    def keys_of_list(self, list):
        return [d['field_name'] for d in list]

    def add_pre_actions(self):
        # self.addAction(QAction('UnSort', self))
        # self.addSeparator()
        self.add_ascend_descend()

    def action_toggled(self, checked):
        if checked:
            # print self.selectedFieldNames
            # print self.sender().field_name
            new_sort = {'field_name':str(self.sender().field_name),
                                     'reverse':self.selectedFieldNames[0]['reverse']}
            self.selectedFieldNames[0].update(new_sort)
            # print self.selectedFieldNames
            self.actionChanged.emit([new_sort])
            for action in self.allFieldActions:
                if action.isChecked() and action != self.sender():
                    self.check_action(action, False)
        else:
            self.check_action(self.sender())

    def ascend_triggered(self, checked):
        if checked:
            # print 'ascend_triggered: field_name:', self.selectedFieldNames
            new_sort = {'field_name': self.selectedFieldNames[0]['field_name'],
                        'reverse': False}
            self.selectedFieldNames[0].update(new_sort)
            self.actionChanged.emit([new_sort])
            self.check_descend(False)

    def descend_triggered(self, checked):
        if checked:
            # print 'descend_triggered: ', self.selectedFieldNames
            new_sort = {'field_name': self.selectedFieldNames[0]['field_name'],
                        'reverse': True}
            self.selectedFieldNames[0].update(new_sort)
            # print 'descend_triggered: ', self.selectedFieldNames
            self.actionChanged.emit([new_sort])
            self.check_ascend(False)
