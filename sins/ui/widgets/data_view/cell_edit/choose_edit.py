# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import *
from .basic import CellWidget
from sins.utils.color import int10_to_rgb
from sins.utils.res import resource
from sins.db.models import Status, File, Department, PermissionGroup, prefetch
from sins.utils.python import get_class_from_name_data
from sins.ui.utils.const import scrollbar_style


# choose
def get_choose(choose_list, value):
    for i in choose_list:
        if i.value == value:
            return i
    return None


class ChooseModel(object):
    def __init__(self,
                 value='',
                 display_text=None,
                 choose_text_list=[],
                 icon=None,
                 color=None,
                 tooltip=None):
        super(ChooseModel, self).__init__()
        self.value = value
        self.display_text = display_text if display_text is not None else value
        self.choose_text_list = choose_text_list
        self.icon = icon
        self.color = color
        self.tooltip = tooltip if tooltip is not None else value

    def __cmp__(self, other):
        return cmp(self.value, other.value)


class ChooseItem(QWidget):
    choose = Signal(str)

    def __init__(self, value, text_list=[], icon=None, icon_size=40, parent=None):
        """
        :param value: str
        :param text_list: [{'text':'', 'width':40}, {}]
        :param icon: str
        :param parent:
        """
        super(ChooseItem, self).__init__(parent)
        self.value = value

        self.masterLayout = QHBoxLayout()
        # if icon is not None:
        self.icon = QLabel()
        self.icon.setFixedSize(icon_size, icon_size)
        if icon is not None and os.path.exists(icon):
            self.icon.setPixmap(resource.get_pixmap(icon, scale=icon_size))
        self.masterLayout.addWidget(self.icon)
        if icon is not None:
            self.masterLayout.insertSpacing(0, 10)
            self.masterLayout.insertSpacing(2, 10)
        for text in text_list:
            label = QLabel(text['text'])
            if text['width'] is not None:
                label.setFixedWidth(text['width'])
            self.masterLayout.addWidget(label)
        self.masterLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.masterLayout)

    def mouseReleaseEvent(self, *args, **kwargs):
        self.choose.emit(self.value)


class CellChooseEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellChooseEdit, self).__init__(**kwargs)

        self.iconSize = 20

        self.iconLabel = QLabel()
        self.iconLabel.setFixedSize(self.iconSize, self.iconSize)
        self.textLabel = QLabel()
        self.masterLayout = QHBoxLayout()
        self.masterLayout.setContentsMargins(0, 0, 0, 0)
        self.masterLayout.setAlignment(Qt.AlignLeft)
        self.masterLayout.addWidget(self.iconLabel)
        self.masterLayout.addWidget(self.textLabel)
        self.setLayout(self.masterLayout)

        self.combo = None

        self.data_value = ''
        self.chooseList = None
        self.chooseListFunc = ''
        self.chooseListFuncArgs = {}
        self.comboWidth = 200
        self.comboHeight = 50
        self.comboIconSize = 40

    def apply_choose(self, choose):
        if choose:
            display_text = choose.display_text
            icon = choose.icon
            color = choose.color
            # print color
            self.textLabel.setText(display_text)
            if icon is not None and os.path.exists(icon):
                self.iconLabel.setPixmap(resource.get_pixmap(icon, scale=self.iconSize))
            if color is not None:
                r, g, b, a = int10_to_rgb(color, max=255, alpha_index=0)
                # print r, g, b, a
                self.back.setStyleSheet('background:rgb({}, {}, {}, {})'.format(r, g, b, 100))
            self.setToolTip(choose.tooltip)
        else:
            self.textLabel.setText(choose)

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            choose = get_choose(self.chooseList, value)
            self.apply_choose(choose)

    def set_editable(self):
        self.combo = QComboBox(self)
        self.comboListWidget = QListWidget()
        self.combo.setModel(self.comboListWidget.model())
        self.combo.setView(self.comboListWidget)
        self.comboListWidget.setStyleSheet(scrollbar_style)
        self.combo.setStyleSheet("""
        *{
            outline:0px;
            /*border:none;*/
        }
        QAbstractItemView{
            min-width:%spx;
            border:none;
        }
        QAbstractItemView::item{
            height:%spx;
        }
        QListView::item{
            background:white;
        }
        QListView::item:hover{
            background:rgb(200,200,200);
        }
        """ % (self.comboWidth, self.comboHeight))
        self.comboListWidget.clear()
        self.chooseList = get_class_from_name_data(__name__, self.chooseListFunc)(**self.chooseListFuncArgs)
        self.chooseList.sort()
        for choose in self.chooseList:
            listItemWidget = ChooseItem(value=choose.value,
                                        text_list=choose.choose_text_list,
                                        icon=choose.icon,
                                        icon_size=self.comboIconSize)
            listItemWidget.choose.connect(self.choose_item)
            listItem = QListWidgetItem()
            self.comboListWidget.addItem(listItem)
            self.comboListWidget.setItemWidget(listItem, listItemWidget)
        self.combo.setFixedSize(self.width(), self.height())
        self.combo.showPopup()

    def choose_item(self, value):
        self.data_value = value
        choose = get_choose(self.chooseList, value)
        self.apply_choose(choose)
        self.edit_finished()

    def set_no_editable(self):
        self.combo.hidePopup()


def get_sex_choose_list():
    return [
        ChooseModel(value='male',
                    choose_text_list=[{'text':'male', 'width':None}],
                    icon=resource.get_pic('icon', 'male.png')),
        ChooseModel(value='female',
                    choose_text_list=[{'text':'female', 'width':None}],
                    icon=resource.get_pic('icon', 'female.png')),
    ]


SexChooseList = get_sex_choose_list()


class SexChooseEdit(CellChooseEdit):
    def __init__(self, **kwargs):
        super(SexChooseEdit, self).__init__(**kwargs)
        self.iconLabel.setVisible(False)
        self.masterLayout.insertSpacing(1, 5)
        self.chooseList = SexChooseList
        self.chooseListFunc = 'get_sex_choose_list'
        self.comboWidth = 100
        self.comboHeight = 30
        self.comboIconSize = 20


def get_department_choose_list():
    choose_list = []
    for department in Department.select():
        name = department.code
        full_name = department.full_name
        color = department.color
        choose_list.append(ChooseModel(
            value=name,
            choose_text_list=[{'text': name, 'width': 40}, {'text': full_name, 'width': None}],
            color=color,
            icon=resource.get_pic('icon', 'Departments.png'),
            tooltip=full_name)
        )
    return choose_list


DepartmentChooseList = get_department_choose_list()


class DepartmentChooseEdit(CellChooseEdit):
    def __init__(self, **kwargs):
        super(DepartmentChooseEdit, self).__init__(**kwargs)
        # self.iconLabel.setVisible(False)
        # self.masterLayout.insertSpacing(1, 5)
        self.chooseList = DepartmentChooseList
        self.chooseListFunc = 'get_department_choose_list'
        self.comboWidth = 200
        self.comboHeight = 30
        self.comboIconSize = 10


def get_permission_group_choose_list():
    choose_list = []
    for permission in PermissionGroup.select():
        name = permission.code
        choose_list.append(ChooseModel(
            value=name,
            choose_text_list=[{'text': name, 'width': None}],
        )
        )
    return choose_list


PermissionGroupChooseList = get_permission_group_choose_list()


class PermissionGroupChooseEdit(CellChooseEdit):
    def __init__(self, **kwargs):
        super(PermissionGroupChooseEdit, self).__init__(**kwargs)
        self.iconLabel.setVisible(False)
        self.masterLayout.insertSpacing(1, 5)
        self.chooseList = PermissionGroupChooseList
        self.chooseListFunc = 'get_permission_group_choose_list'
        self.comboWidth = 120
        self.comboHeight = 30
        self.comboIconSize = 10


def get_all_status():
    choose_list = {}
    for status in prefetch(Status.select(), File):
        for model in ['Project', 'Sequence', 'Shot', 'Asset', 'Task', 'Version']:
            if model not in choose_list.keys():
                choose_list[model] = []
            if status.referred_table.find(model) != -1:
                name = status.name
                full_name = status.full_name
                color = status.color
                icon = status.thumbnail.host_path
                choose_list[model].append(ChooseModel(
                    value=name,
                    choose_text_list=[{'text': name, 'width': 50}, {'text': full_name, 'width': None}],
                    color=color,
                    icon=icon,
                )
                )
    return choose_list


all_status_choose = get_all_status()


def get_status_choose_list(model=''):
    if model in all_status_choose:
        return all_status_choose[model]


loaded_project_status = get_status_choose_list(model='Project')
loaded_sequence_status = get_status_choose_list(model='Sequence')
loaded_shot_status = get_status_choose_list(model='Shot')
loaded_asset_status = get_status_choose_list(model='Asset')
loaded_task_status = get_status_choose_list(model='Task')
loaded_version_status = get_status_choose_list(model='Version')


class StatusChooseEdit(CellChooseEdit):
    def __init__(self, model=None, **kwargs):
        super(StatusChooseEdit, self).__init__(**kwargs)
        self.textLabel.setVisible(False)
        self.masterLayout.insertSpacing(1, 5)
        self.masterLayout.setAlignment(Qt.AlignCenter)
        # self.chooseList = get_status_choose_list()
        self.chooseListFunc = 'get_status_choose_list'
        self.chooseListFuncArgs = {'model': model}
        self.chooseList = get_class_from_name_data('sins.ui.widgets.data_view.cell_edit',
                                                              'loaded_{}_status'.
                                                              format(model.lower()))
        self.comboWidth = 250
        self.comboHeight = 50
        self.comboIconSize = 20

