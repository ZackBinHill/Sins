# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/30/2018

# from sins.db.models import *
from sins.ui.widgets.data_view.cell_edit import *
from sins.module.time_utils import datetime_to_date


DEFAULT_INNER_WIDGET = CellLineEdit
DEFAULT_COLUMN_WIDTH = 100


class InField(object):
    def __init__(self,
                 name='',
                 label='',
                 model_attr=None,
                 inner_widget=DEFAULT_INNER_WIDGET,
                 widget_attr_map={},
                 column_width=100,
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
        self.in_fields = []
        self.out_fields = []
        self.default_fields = []
        self.default_filters = ''
        self.default_sort = [{'field_name': '{}>created_date'.format(self.config_name), 'reverse': False}]
        self.default_groups = []

    def refine_default_fields(self):
        for index, field_name in enumerate(self.default_fields):
            if len(field_name.split('>')) == 1:
                field_name = self.config_name + '>' + field_name
                self.default_fields[index] = field_name
        # print self.default_fields

    def first_fields(self):
        field_list = []
        field_list.extend(self.origin_fields)
        field_list.extend(self.in_fields)
        return field_list

    def find_out_field(self, field_name):
        for field in self.out_fields:
            if field.name == field_name:
                return field

    def find_field(self, field_name):
        split_list = field_name.split('>')
        # print split_list
        if len(split_list) == 1:
            for field in self.first_fields():
                if field.name == field_name:
                    field.parent_configs = [self.config_name]
                    return field
        elif len(split_list) == 2:
            for field in self.first_fields():
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
    def __init__(self, db_model=None, connection_model=None, prefetch_config = []):
        super(PrefetchConfig, self).__init__()

        self.db_model = db_model
        self.connection_model = connection_model
        self.prefetch_config = prefetch_config


class DepartmentConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(DepartmentConfig, self).__init__(config_name='department', **kwargs)

        self.db_model = Department
        self.in_fields = [
            InField(name='code', label='Code', edit_permission=['Root']),
            InField(name='full_name', label='Full Name', edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
            InField(name='description', label='Description', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
            InField(name='color', label='Color', inner_widget=CellColorEdit, edit_permission=['Root'],
                    group_enable=False),

            InField(name='persons', label='Persons', model_attr='person_objects',
                    inner_widget=CellMultiObjectEdit, widget_attr_map={'linkable': False, 'link_model': 'Person'},
                    edit_permission=['Root'], group_enable=False, sort_enable=False),
        ]
        self.prefetch_config = [
            PrefetchConfig(db_model=Person, ),
        ]

        self.default_fields = ['code',
                               'full_name',
                               'description',
                               'color',
                               'persons',
                               ]

        self.refine_default_fields()


class PermissionGroupConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(PermissionGroupConfig, self).__init__(config_name='permission_group', **kwargs)

        self.db_model = PermissionGroup
        self.in_fields = [
            InField(name='code', label='Code'),
            InField(name='description', label='Description', inner_widget=CellTextEdit,
                    group_enable=False, sort_enable=False),
        ]
        # self.out_fields = [
        #     OutField(name='department', field_label='Department', config=DepartmentConfig()),
        # ]
        self.default_fields = ['code',
                               'description',
                               ]

        self.refine_default_fields()


class PersonConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(PersonConfig, self).__init__(config_name='person', **kwargs)

        self.db_model = Person
        self.in_fields = [
            InField(name='user_login', label='Login', group_enable=False),
            InField(name='user_pwd', label='Password', inner_widget=PasswordEdit,
                    group_enable=False, sort_enable=False),
            InField(name='first_name', label='First Name', edit_permission=['Root']),
            InField(name='last_name', label='Last Name', edit_permission=['Root']),
            InField(name='cn_name', label='CN Name', edit_permission=['Root'], group_enable=False, sort_enable=False),
            InField(name='sex', label='Sex', inner_widget=SexChooseEdit, column_width=50, edit_permission=['Root']),
            InField(name='email', label='Email', edit_permission=['Root'], group_enable=False, sort_enable=False),
            InField(name='thumbnail', label='Thumbnail', inner_widget=CellThumbnail, edit_permission=['Root', 'Artist'],
                    column_width=70, group_enable=False, sort_enable=False),
            InField(name='active', label='Status', inner_widget=ActiveBoolEdit, edit_permission=['Root'],
                    column_width=70),
            InField(name='join_date', label='Join Date',
                    inner_widget=CellDateEdit, edit_permission=['Root'],),
            InField(name='leave_date', label='Leave Date', inner_widget=CellDateEdit, edit_permission=['Root']),

            InField(name='department', label='Department', model_attr='department_name',
                    inner_widget=DepartmentChooseEdit, edit_permission=['Root'],
                    group_attr=[Department, 'code']),
            InField(name='permission_group', label='Permission Group', model_attr='permission_group_name',
                    inner_widget=PermissionGroupChooseEdit, edit_permission=['Root'],
                    group_attr=[PermissionGroup, 'code']),

            InField(name='projects', label='Projects', model_attr='project_objects',
                    inner_widget=CellMultiObjectEdit, widget_attr_map={'linkable': False, 'link_model': 'Project'},
                    edit_permission=['Root'], group_enable=False),
            InField(name='groups', label='Groups', model_attr='group_objects',
                    inner_widget=CellMultiObjectEdit, widget_attr_map={'link_model': 'Group'},
                    edit_permission=['Root'], group_enable=False),
        ]
        self.out_fields = [
            OutField(field_label='Department', config=DepartmentConfig()),
            OutField(field_label='PermissionGroup', config=PermissionGroupConfig()),
        ]
        self.prefetch_config = [
            DepartmentConfig(),
            PermissionGroupConfig(),
            ProjectConfig(connection_model=ProjectPersonConnection),
            GroupConfig(connection_model=GroupPersonConnection),
        ]
        self.default_fields = ['person>thumbnail',
                               'person>user_login',
                               'person>user_pwd',
                               'person>first_name',
                               'person>last_name',
                               'person>cn_name',
                               'person>email',
                               'person>active',
                               'person>join_date',
                               'person>department',
                               'person>permission_group',
                               'person>projects',
                               'person>groups',
                               # 'person>department>name',
                               ]
        self.default_groups = []
        self.default_sort = [{'field_name': 'person>user_login', 'reverse': False}]


class StatusConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(StatusConfig, self).__init__(config_name='status', **kwargs)

        self.db_model = Status
        self.in_fields = [
            InField(name='name', label='Name', model_attr='name', edit_permission=['Root']),
            InField(name='full_name', label='Full Name', model_attr='full_name', edit_permission=['Root'],
                    group_enable=False),
            InField(name='description', label='Description', inner_widget=CellTextEdit,
                    group_enable=False, edit_permission=['Root']),
            InField(name='color', label='Color', inner_widget=CellColorEdit, edit_permission=['Root'],
                    group_enable=False),
        ]
        self.default_fields = ['name',
                               'full_name',
                               'color',
                               ]

        self.refine_default_fields()


class ProjectConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(ProjectConfig, self).__init__(config_name='project', **kwargs)

        self.db_model = Project
        self.in_fields = [
            InField(name='code', label='Code'),
            InField(name='full_name', label='Full Name', group_enable=False, edit_permission=['Root']),
            InField(name='description', label='Description', inner_widget=CellTextEdit,
                    group_enable=False, edit_permission=['Root']),
            # InField(name='status', label='Status', inner_widget=ProjectStatusChooseEdit, edit_permission=['Root']),
            InField(name='status', label='Status',
                    inner_widget=StatusChooseEdit, widget_attr_map={'model': 'Project'},
                    edit_permission=['Root']),
            InField(name='thumbnail', label='Thumbnail', inner_widget=CellThumbnail, edit_permission=['Root'],
                    column_width=70, group_enable=False, sort_enable=False),
            InField(name='start_time', label='Start Time', inner_widget=CellDateEdit, edit_permission=['Root']),
            InField(name='end_time', label='End Time', inner_widget=CellDateEdit, edit_permission=['Root']),
        ]
        self.default_fields = ['thumbnail',
                               'status',
                               'code',
                               'full_name',
                               'description',
                               'start_time',
                               'end_time',
                               ]

        self.refine_default_fields()


class GroupConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(GroupConfig, self).__init__(config_name='group', **kwargs)

        self.db_model = Group
        self.in_fields = [
            InField(name='code', label='Code', edit_permission=['Root']),
            InField(name='full_name', label='Full Name', group_enable=False,
                    edit_permission=['Root']),
            InField(name='description', label='Description', inner_widget=CellTextEdit,
                    edit_permission=['Root'], group_enable=False),
        ]
        self.default_fields = ['code',
                               'full_name',
                               'description',
                               ]

        self.refine_default_fields()


class PipelineStepConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(PipelineStepConfig, self).__init__(config_name='pipeline_step', **kwargs)

        self.db_model = PipelineStep
        self.in_fields = [
            InField(name='name', label='Name', edit_permission=['Root']),
            InField(name='full_name', label='Full Name', edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
            InField(name='description', label='Description', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
            InField(name='color', label='Color', inner_widget=CellColorEdit, edit_permission=['Root'],
                    group_enable=False),
        ]
        self.default_fields = ['name',
                               'full_name',
                               'description',
                               'color',
                               ]

        self.refine_default_fields()


class SequenceConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(SequenceConfig, self).__init__(config_name='sequence', **kwargs)

        self.db_model = Sequence
        self.in_fields = [
            InField(name='name', label='Name', edit_permission=['Root']),
            InField(name='description', label='Description', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
        ]
        self.default_fields = ['name',
                               'description',
                               ]
        self.out_fields = [
            OutField(field_label='Project', config=ProjectConfig()),
        ]
        self.prefetch_config = [
            ProjectConfig(),
        ]

        self.refine_default_fields()


class AssetTypeConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(AssetTypeConfig, self).__init__(config_name='asset_type', **kwargs)

        self.db_model = AssetType
        self.in_fields = [
            InField(name='name', label='Name', edit_permission=['Root']),
            InField(name='description', label='Description', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
        ]
        self.default_fields = ['name',
                               'description',
                               ]
        self.out_fields = [
            OutField(field_label='Project', config=ProjectConfig()),
        ]
        self.prefetch_config = [
            ProjectConfig(),
        ]

        self.refine_default_fields()


class TagConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(TagConfig, self).__init__(config_name='tag', **kwargs)

        self.db_model = Tag
        self.in_fields = [
            InField(name='name', label='Name', edit_permission=['Root']),
            InField(name='description', label='Description', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
        ]
        self.default_fields = ['name',
                               'description',
                               ]
        self.out_fields = [
            OutField(field_label='Project', config=ProjectConfig()),
        ]
        self.prefetch_config = [
            ProjectConfig(),
        ]

        self.refine_default_fields()


class AssetConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(AssetConfig, self).__init__(config_name='asset', **kwargs)

        self.db_model = Asset
        self.in_fields = [
            InField(name='name', label='Name', edit_permission=['Root']),
            InField(name='description', label='Description', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
            # InField(name='status', label='Status', inner_widget=AssetStatusChooseEdit, edit_permission=['Root']),
            InField(name='status', label='Status',
                    inner_widget=StatusChooseEdit, widget_attr_map={'model': 'Asset'},
                    edit_permission=['Root']),
            InField(name='thumbnail', label='Thumbnail', inner_widget=CellThumbnail, edit_permission=['Root'],
                    column_width=70, group_enable=False, sort_enable=False),
            InField(name='asset_type', label='Asset Type', model_attr='asset_type_object',
                    inner_widget=CellSingleObjectEdit),
        ]
        self.default_fields = ['thumbnail',
                               'name',
                               'description',
                               'status',
                               'asset_type',
                               ]
        self.out_fields = [
            OutField(field_label='Project', config=ProjectConfig()),
            OutField(field_label='Asset Type', config=AssetTypeConfig()),
        ]
        self.prefetch_config = [
            ProjectConfig(),
            AssetTypeConfig(),
        ]

        self.refine_default_fields()


class ShotConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(ShotConfig, self).__init__(config_name='shot', **kwargs)

        self.db_model = Shot
        self.in_fields = [
            InField(name='name', label='Name', edit_permission=['Root']),
            InField(name='description', label='Description', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
            InField(name='requirement', label='Requirement', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
            # InField(name='status', label='Status', inner_widget=AssetStatusChooseEdit, edit_permission=['Root']),
            InField(name='status', label='Status',
                    inner_widget=StatusChooseEdit, widget_attr_map={'model': 'Shot'},
                    edit_permission=['Root']),
            InField(name='thumbnail', label='Thumbnail', inner_widget=CellThumbnail, edit_permission=['Root'],
                    column_width=70, group_enable=False, sort_enable=False),
            InField(name='fps', label='Fps', edit_permission=['Root']),
            InField(name='head_in', label='Head In', edit_permission=['Root']),
            InField(name='tail_out', label='Tail Out', edit_permission=['Root']),
            InField(name='duration', label='Duration', edit_permission=['Root']),
            InField(name='final_delivery', label='Final Delivery', inner_widget=CellDateEdit, edit_permission=['Root']),

            InField(name='sequence', label='Sequence', model_attr='sequence_object',
                    inner_widget=CellSingleObjectEdit),
        ]
        self.out_fields = [
            OutField(name='project', field_label='Project', config=ProjectConfig()),
            OutField(name='sequence', field_label='Sequence', config=SequenceConfig()),
        ]
        self.prefetch_config = [
            ProjectConfig(),
            SequenceConfig(),
        ]
        self.default_fields = [
            'thumbnail',
            'id',
            'name',
            'status',
            'description',
            'requirement',
            'fps',
            'head_in',
            'tail_out',
            'final_delivery',
            'sequence',
        ]

        self.refine_default_fields()

        self.default_groups = [
            # {'field_name': 'shot>sequence>name', 'reverse': False},
        ]


class TaskConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(TaskConfig, self).__init__(config_name='task', **kwargs)

        self.db_model = Task
        self.in_fields = [
            InField(name='name', label='Name', edit_permission=['Root']),
            InField(name='description', label='Description', inner_widget=CellTextEdit, edit_permission=['Root'],
                    group_enable=False, sort_enable=False),
            # InField(name='status', label='Status', inner_widget=AssetStatusChooseEdit, edit_permission=['Root']),
            InField(name='status', label='Status',
                    inner_widget=StatusChooseEdit, widget_attr_map={'model': 'Task'},
                    edit_permission=['Root']),
            InField(name='thumbnail', label='Thumbnail', inner_widget=CellThumbnail, edit_permission=['Root'],
                    column_width=70, group_enable=False, sort_enable=False),
            InField(name='begin_date', label='Begin Date', inner_widget=CellDateEdit, edit_permission=['Root']),
            InField(name='end_date', label='End Date', inner_widget=CellDateEdit, edit_permission=['Root']),
            InField(name='planned_time', label='Planned Time', inner_widget=CellTimedeltaEdit, edit_permission=['Root']),
            InField(name='link', label='Link', model_attr='link_object',
                    inner_widget=CellSingleObjectEdit),
            InField(name='step', label='Step', model_attr='step_object',
                    inner_widget=CellSingleObjectEdit),
        ]
        self.default_fields = ['thumbnail',
                               'name',
                               'status',
                               'description',
                               'begin_date',
                               'end_date',
                               'planned_time',
                               'link',
                               'step',
                               ]

        self.refine_default_fields()


