# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/30/2018

from .config import *


class DepartmentConfig(ModelConfig):
    def __init__(self, **kwargs):
        super(DepartmentConfig, self).__init__(config_name='department', **kwargs)

        self.db_model = Department
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
            InField(name='user_login', label='Login', group_enable=False),
            InField(name='user_pwd', label='Password', widget_attr_map={'password_mode': True},
                    group_enable=False, sort_enable=False),
            InField(name='first_name', label='First Name', edit_permission=['Root']),
            InField(name='last_name', label='Last Name', edit_permission=['Root']),
            InField(name='cn_name', label='CN Name', edit_permission=['Root'], group_enable=False, sort_enable=False),
            InField(name='sex', label='Sex', inner_widget=SexChooseEdit, column_width=50, edit_permission=['Root']),
            InField(name='email', label='Email', edit_permission=['Root'], group_enable=False, sort_enable=False),
            InField(name='thumbnail', label='Thumbnail', inner_widget=CellThumbnail, edit_permission=['Root', 'Artist'],
                    column_width=70, group_enable=False, sort_enable=False),
            InField(name='active', label='Status',
                    inner_widget=CellBoolEdit,
                    widget_attr_map={'true_text': '<font color=green>active</font>',
                                     'false_text': '<font color=red><SPAN style="TEXT-DECORATION: line-through">'
                                                   'active</SPAN></font>'},
                    edit_permission=['Root'], column_width=70),
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
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
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
        self._in_fields = [
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


