# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/7/2018

from sins.utils.log import log_cost_time
from sins.config.data_view_configs import *
from sins.config.utils import DataItem, DataGroup, get_prefetch_models
from sins.ui.widgets.label import QLabelButton
from sins.db.permission import is_editable
from .const import FOREIGN_POPULATE_DEPTH
from .menu import SortMenu, FieldsMenu, GroupMenu
from .load import LoadThread, LoadingLabel
import copy
import math
import time


logger = get_logger(__name__)

EDITLABEL_SIZE = 20
ItemsPerPage = 0


class PageLabelButton(QLabelButton):
    def __init__(self, name):
        colorDict = {
            "normalcolor": "darkgray",
            "hovercolor": "darkgray",
            "clickcolor": "darkgray",
            "normalbackcolor": "transparent",
            "hoverbackcolor": "rgb(200,200,200)",
            "clickbackcolor": "darkgray"
        }
        super(PageLabelButton, self).__init__(name, colorDict=colorDict, scale=24)


class BaseTree(QTreeWidget):
    addItemField = Signal(int)

    def __init__(self, config=None, db_model=None, parent=None):
        super(BaseTree, self).__init__(parent)

        self.config = config
        self.db_model = db_model
        self.basic_filter = []

        self.showFields = []
        self.showFieldNames = []
        self.dataItems = []
        self.tempItemFields = []
        self.tempItemWidgets = []

        self.currentGroups = []
        self.currentSorts = []
        self.currentPageNumber = 1
        self.currentItemsPerPage = 50

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.set_style()

        self.loadThread = LoadThread(self)
        self.loadThread.loadFinish.connect(self.refresh)

        self.itemSelectionChanged.connect(self.item_select_changed)
        self.header().sectionResized.connect(self.section_resized)
        self.addItemField.connect(self.add_item_field, Qt.QueuedConnection)

    def init_ui(self):
        self.setColumnCount(len(self.config.default_fields) + 1)
        self.setColumnWidth(0, 20)
        self.showFieldNames = copy.deepcopy(self.config.default_fields)
        self.headItem = QTreeWidgetItem()
        for index, fieldname in enumerate(self.config.default_fields):
            field = self.config.find_field(fieldname)
            self.headItem.setText(index + 1, '{}{}'.format(field.label_prefix, field.label))
            self.setColumnWidth(index + 1, field.column_width)
            self.showFields.append(field)
        self.setHeaderItem(self.headItem)
        self.header().setStretchLastSection(False)

    def set_basic_filter(self, basic_filter):
        self.basic_filter = basic_filter

    def get_field_data(self, data, config, db_instance=None, prefix=None, populate_depth=FOREIGN_POPULATE_DEPTH):
        # print db_instance
        if db_instance is not None:
            prefix = '{}>{}'.format(prefix, config.config_name) if prefix is not None else config.config_name
            for index, field in enumerate(config.first_fields):
                # data.update({'{}>{}'.format(prefix, field.name): getattr(db_instance, field.model_attr)})
                data.update({'{}>{}'.format(prefix, field.name): {'value': getattr(db_instance, field.model_attr),
                                                                  'db_instance': db_instance}})
            if populate_depth > 0:
                for out_field in config.out_fields:
                    # print out_field.model_attr, getattr(db_instance, out_field.model_attr)
                    self.get_field_data(data,
                                   out_field.config,
                                   db_instance=getattr(db_instance, out_field.model_attr),
                                   prefix=prefix,
                                   populate_depth=populate_depth - 1)

    @log_cost_time
    def load_data(self,
                  group_field_names=None,
                  sort_field_names=None,
                  page_number=None,
                  items_per_page=None):
        # print group_field_names, sort_field_names

        self.currentGroups = group_field_names if group_field_names is not None else self.currentGroups
        self.currentSorts = sort_field_names if sort_field_names is not None else self.currentSorts
        # if isinstance(sort_field_names, list) and len(sort_field_names) > 0:
        #     self.currentSorts = sort_field_names[0]
        # elif isinstance(sort_field_names, dict):
        #     self.currentSorts = sort_field_names
        self.currentPageNumber = page_number if page_number is not None else self.currentPageNumber
        self.currentItemsPerPage = items_per_page if items_per_page is not None else self.currentItemsPerPage

        # print self.currentGroups, self.currentSorts

        self.setColumnWidth(0, 20 * (len(self.currentGroups) + 1))
        self.rootDataGroup = DataGroup()
        if self.db_model:
            query = self.db_model.select()

            # filter
            for each_filter in self.basic_filter:
                if each_filter['join'] is not None:
                    query = query.switch(self.db_model).join(each_filter['join']).where(each_filter['where'])
                else:
                    query = query.switch(self.db_model).where(each_filter['where'])

            # order---group>>order
            all_order_field_list = copy.deepcopy(self.currentGroups)
            all_order_field_list.extend(self.currentSorts)

            joined_model = []

            for order_field in all_order_field_list:
                # if 'field' not in order_field:
                order_field['field'] = self.config.find_field(order_field['field_name'])
                # print 'find:', order_field['field_name'], order_field['field']

                field = order_field['field']
                field_name = order_field['field_name']
                reverse = order_field['reverse']

                parent_configs = field.parent_configs

                # print field, field_name, reverse, parent_configs

                if len(parent_configs) <= 1:
                    group_attr = field.group_attr
                    # print group_attr
                    if isinstance(group_attr, str):
                        if reverse:
                            query = query.order_by_extend(getattr(self.db_model, group_attr).desc())
                        else:
                            query = query.order_by_extend(getattr(self.db_model, group_attr))
                    elif isinstance(group_attr, list):
                        for model in group_attr[:-1]:
                            # print model
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
                    current_config = self.config
                    query = query.switch(self.db_model)
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
            # paginate
            if self.currentItemsPerPage != -1:
                all_page_numbers = int(math.ceil(query.count() / float(self.currentItemsPerPage)))
                self.parent().allPagesLabel.setText('of {}'.format(all_page_numbers))
                self.parent().allPageNum = all_page_numbers
                self.parent().currentPageValidator.setTop(all_page_numbers)
                query = query.paginate(self.currentPageNumber, self.currentItemsPerPage)
                # query = query.limit(50)
            else:
                self.parent().allPagesLabel.setText('of 1')
                self.parent().allPageNum = 1

            # prefetch
            for prefetch_model in get_prefetch_models(self.config, depth=FOREIGN_POPULATE_DEPTH):
                prefetch(query, *prefetch_model)

            for row in query:
                data = {}
                # print row.id, row.sequence.name
                # data.update({'object': row})
                self.get_field_data(data, self.config, db_instance=row)
                self.rootDataGroup.append(DataItem(data))
                # print data
            for group_field_name in self.currentGroups:
                # print group_field_name
                self.rootDataGroup.group_by(**group_field_name)
            for order_field_name in self.currentSorts:
                # print group_field_name
                self.rootDataGroup.sort_by(**order_field_name)
            # print self.currentSorts
            # if self.currentSorts is not None:
            #     self.rootDataGroup.sort_by(**self.currentSorts)
        else:
            logger.warning('must load config first!')

        # time.sleep(5)

    def add_item_field(self, index):
        items_each_add = self.columnCount()
        if index < len(self.tempItemFields):
            for i in range(index, index + items_each_add):
                if i < len(self.tempItemFields):
                    item = self.tempItemFields[i]
                    try:
                        self.add_field(item[0], item[1], item[2], item[3])
                    except RuntimeError:
                        pass
            self.addItemField.emit(index + items_each_add)
        else:
            for i in range(self.columnCount()):
                self.section_resized(i)
            self.updateGeometries()
            self.tempItemFields = []
            self.parent().loadingLabel.set_loading(False)
            logger.debug('refresh cost time: {}'.format(time.time() - self.refresh_start_time))

    # @log_cost_time
    def refresh(self, sort_field=None):
        self.refresh_start_time = time.time()
        self.clear()
        self.dataItems = []
        # QApplication.setOverrideCursor(Qt.WaitCursor)
        self.add_groups(self.rootDataGroup, parent=self)
        # self.add_temp_item_field()
        self.addItemField.emit(0)
        # self.set_item_widget()
        # for index, field in enumerate(self.showFields):
        #     print index, field.name
        #     # self.setColumnWidth(index + 1, field.column_width)
        #     self.section_resized(index + 1, newsize=field.column_width)
        # QApplication.restoreOverrideCursor()
        self.parent().loadingLabel.set_loading(False)

    def add_field(self, item, index, field, data):
        field_name = ''
        for config_name in field.parent_configs:
            field_name += '{}>'.format(config_name)
        field_name += field.name

        # cellWidgetName = field.inner_widget
        # # editable = True if current_permission in field.edit_permission else False
        # # editable = is_editable(field, data, field_name)
        # cellWidget = cellWidgetName(treeitem=item,
        #                             column=index,
        #                             model_attr=field.model_attr,
        #                             column_label=field.label,
        #                             parent=self,
        #                             **field.widget_attr_map)
        # # print 'add field:', cellWidget, child.data[field.name]
        cellWidget = field.create_widget(treeitem=item, column=index, parent=self)

        if field_name in data.keys():
            cellWidget.set_value(data[field_name]['value'])
            cellWidget.set_db_instance(data[field_name]['db_instance'])
            cellWidget.set_read_only(is_editable(editable_permission=field.edit_permission,
                                                 db_instance=data[field_name]['db_instance']))
        # if not field.readonly:
        #     cellWidget.add_front()
        self.setItemWidget(item, index, cellWidget)
        # self.tempItemWidgets.append([item, index, cellWidget])

    def add_groups(self, group, parent=None):
        # print group, parent
        if group.field_name is not None:
            group_item = QTreeWidgetItem()
            field = self.config.find_field(group.field_name)
            value = field.label_prefix + field.label + '>' + str(group.field_value if group.field_value is not None else 'None')
            group_item.setText(0, value)
            if parent == self:
                self.addTopLevelItem(group_item)
            else:
                parent.addChild(group_item)
            self.setFirstItemColumnSpanned(group_item, True)
            group_item.setExpanded(True)
        else:
            group_item = self

        for child in group.children():
            if isinstance(child, DataItem):
                item = QTreeWidgetItem()
                if group_item == self:
                    self.addTopLevelItem(item)
                else:
                    group_item.addChild(item)
                for index, field in enumerate(self.showFields):
                    # self.add_field(item, index + 1, field, child.data)
                    self.tempItemFields.append([item, index + 1, field, child.data])
                self.dataItems.append(item)
                setattr(item, 'tree', self)
                setattr(item, 'instance_data', child.data)
            else:
                self.add_groups(child, parent=group_item)

    def set_style(self):
        style = """
        *{
            outline:0px
        }
        QTreeWidget::item{
            background:rgb(220, 250, 220);
            border-right: 1px solid gray;
            border-bottom: 1px solid gray;
        }
        QTreeWidget::item:selected{
            background:rgb(200, 220, 255);
        }
        QTreeWidget::item:has-children{
            background:rgb(150, 150, 150);
        }
        QTreeWidget::branch:!has-children:!selected:has-siblings:adjoins-item,
        QTreeWidget::branch:!has-children:!selected:!has-siblings:adjoins-item{
            image:url(%s/icon/unchecked.png);
        }
        QTreeWidget::branch:!has-children:selected:has-siblings:adjoins-item,
        QTreeWidget::branch:!has-children:selected:!has-siblings:adjoins-item{
            image:url(%s/icon/checked.png)
        }
        QTreeWidget::branch:has-children:selected:!has-siblings:adjoins-item,
        QTreeWidget::branch:has-children:selected:has-siblings:adjoins-item{
            image:url(%s/icon/checked.png)
        }
        """
        self.setStyleSheet(style.replace("%s", resource.Res_Folder).replace("\\", "/"))

    def section_resized(self, index=0, oldsize=100, newsize=100):
        # print 'section_resized', index, oldsize, newsize
        for item in self.dataItems:
            if self.itemWidget(item, index) is not None:
                if self.itemWidget(item, index).autoHeight == True:
                    newheight = 0
                    for j in range(self.columnCount()):
                        temp = self.itemWidget(item, j)
                        temph = temp.targetHeight if hasattr(temp, 'targetHeight') else 0
                        newheight = max(newheight, temph)
                        newheight = max(newheight, 25)
                    # print newheight
                    for j in range(self.columnCount()):
                        item.setSizeHint(j, QSize(newsize, newheight))
                    # self.updateGeometries()

    def resize_column(self, width, height):
        if hasattr(self.sender(), "treeitem"):
            treeitem = self.sender().treeitem
            # print treeitem, treeitem.row()
            treeitem.setSizeHint(0, QSize(width, height))
            # QTreeWidgetItem.setSizeHint()
            self.updateEditorGeometries()
            self.updateGeometries()

    def item_select_changed(self):
        for item in self.selectedItems():
            # print item
            for index in range(item.childCount()):
                child = item.child(index)
                child.setSelected(True)

    def add_column(self, field_name):
        field_name = str(field_name)
        # print field_name, field_name in self.showFieldNames, self.columnCount()
        if field_name in self.showFieldNames:
            index = self.showFieldNames.index(field_name)
            self.showColumn(index + 1)
        else:
            field = self.config.find_field(field_name)
            index = self.columnCount()
            # print index
            self.setColumnCount(index + 1)
            self.headItem.setText(index, '{}{}'.format(field.label_prefix, field.label))
            self.setColumnWidth(index, field.column_width)
            for item in self.dataItems:
                # print item.instance_data
                self.add_field(item, index, field, item.instance_data)
            # self.set_item_widget()
            self.showFieldNames.append(field_name)
            self.showFields.append(field)

    def remove_column(self, field_name):
        # print field_name, field_name in self.showFieldNames
        if field_name in self.showFieldNames:
            index = self.showFieldNames.index(field_name)
            self.hideColumn(index + 1)

    def change_column(self, field_name, add=True):
        if add:
            self.add_column(field_name)
        else:
            self.remove_column(field_name)
        print 'change field preference'

    def change_group(self, group_fields):
        # self.load_data(group_field_names=group_fields)
        # self.refresh()
        self.load_and_refresh(group_field_names=group_fields)
        print 'change group preference'

    def change_sort(self, sort_fields):
        # self.load_data(sort_field_name=sort_fields)
        # self.refresh()
        # print 'change_sort:', sort_fields
        self.load_and_refresh(sort_field_names=sort_fields)
        print 'change group preference'

    def start_load_thread(self, group_field_names=None, sort_field_names=None, page_number=None, items_per_page=None):
        self.loadThread.set_attr(group_field_names, sort_field_names, page_number, items_per_page)
        self.loadThread.start()

    def load_and_refresh(self, group_field_names=None, sort_field_names=None, page_number=None, items_per_page=None):
        self.parent().loadingLabel.set_loading(True)
        # QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        # self.load_data(group_field_names, sort_field_names, page_number, items_per_page)
        self.start_load_thread(group_field_names, sort_field_names, page_number, items_per_page)
        # self.refresh()
        # QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        # self.parent().loadingLabel.set_loading(False)


class DataWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(DataWidget, self).__init__(*args, **kwargs)

        self.config = None
        self.db_model = None

        self.allPageNum = 1

        self.init_ui()
        self.set_style()
        self.create_signal()

        self.loadingLabel = LoadingLabel(self)
        self.loadingLabel.set_loading(False)

    def init_ui(self):

        self.addRowBtn = QPushButton('Add')

        self.groupBtn = QToolButton(self)
        self.groupBtn.setText('Group')
        self.groupBtn.setIcon(resource.get_qicon('button', 'Group.png'))

        self.sortBtn = QToolButton(self)
        self.sortBtn.setText('Sort')
        self.sortBtn.setIcon(resource.get_qicon('button', 'Sort.png'))

        self.fieldsBtn = QToolButton(self)
        self.fieldsBtn.setText('Fields')
        self.fieldsBtn.setIcon(resource.get_qicon('button', 'Field.png'))

        self.filterBtn = QToolButton(self)
        self.filterBtn.setText('Filter')
        self.filterBtn.setIcon(resource.get_qicon('button', 'Filter.png'))

        for b in [self.groupBtn, self.sortBtn, self.fieldsBtn, self.filterBtn]:
            b.setPopupMode(QToolButton.InstantPopup)
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.addRowBtn)
        self.buttonLayout.addWidget(self.groupBtn)
        self.buttonLayout.addWidget(self.sortBtn)
        self.buttonLayout.addWidget(self.fieldsBtn)
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.filterBtn)

        self.dataTable = BaseTree(parent=self)

        self.pageLayout = QHBoxLayout()
        self.prePageBtn = PageLabelButton('arrow_left1')
        self.nextPageBtn = PageLabelButton('arrow_right1')
        self.currentPageEdit = QLineEdit('1')
        self.currentPageEdit.setFixedWidth(30)
        self.currentPageValidator = QIntValidator(1, 10)
        self.currentPageEdit.setValidator(self.currentPageValidator)
        self.allPagesLabel = QLabel('of 5')
        self.itemsPerPageCombo = QComboBox()
        self.itemsPerPageCombo.addItems(['3', '10', '20', '50', '100', 'All'])
        self.itemsPerPageCombo.setCurrentIndex(ItemsPerPage)
        # self.itemsPerPageCombo.setEditable(True)
        self.itemsPerPageLabel = QLabel('per page')
        self.pageLayout.addStretch()
        self.pageLayout.addWidget(self.prePageBtn)
        self.pageLayout.addWidget(self.currentPageEdit)
        self.pageLayout.addWidget(self.allPagesLabel)
        self.pageLayout.addWidget(self.nextPageBtn)
        self.pageLayout.addWidget(self.itemsPerPageCombo)
        self.pageLayout.addWidget(self.itemsPerPageLabel)
        self.pageLayout.setAlignment(Qt.AlignRight)

        layout = QVBoxLayout()
        layout.addLayout(self.buttonLayout)
        layout.addWidget(self.dataTable)
        layout.addLayout(self.pageLayout)
        self.setLayout(layout)

        self.groupMenu = GroupMenu(self)
        self.groupBtn.setMenu(self.groupMenu)

        self.sortMenu = SortMenu(self)
        self.sortBtn.setMenu(self.sortMenu)

        self.fieldsMenu = FieldsMenu(self)
        self.fieldsBtn.setMenu(self.fieldsMenu)

    def create_signal(self):
        self.groupMenu.actionChanged.connect(self.dataTable.change_group)
        self.sortMenu.actionChanged.connect(self.dataTable.change_sort)
        self.fieldsMenu.actionChanged.connect(self.dataTable.change_column)

        self.prePageBtn.buttonClicked.connect(self.pre_page_clicked)
        self.nextPageBtn.buttonClicked.connect(self.next_page_clicked)
        self.currentPageEdit.editingFinished.connect(self.current_page_edit)
        self.itemsPerPageCombo.currentIndexChanged.connect(self.item_per_page_changed)

    def set_style(self):
        style = """
                QPushButton,QToolButton{
                    width: 88px;
                    border:1px solid gray;
                    border-radius: 3px
                }
                QPushButton{
                    height:28px;
                }
                QToolButton{
                    height:25px;
                }
                QToolButton::menu-indicator{
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    right: 5px;
                    width: 20px;
                }
                """
        self.setStyleSheet(style.replace("%s", resource.Res_Folder).replace("\\", "/"))

    def load_config(self, config):
        self.config = config
        self.db_model = config.db_model
        self.groupMenu.load_config(config)
        self.sortMenu.load_config(config)
        self.fieldsMenu.load_config(config)
        self.dataTable.config = config
        self.dataTable.db_model = config.db_model
        self.dataTable.init_ui()

    def set_basic_filter(self, basic_filter):
        self.dataTable.set_basic_filter(basic_filter)

    def refresh(self):
        page = None
        item_per_page = None
        try:
            page = int(self.currentPageEdit.text())
        except:
            pass
        try:
            if self.itemsPerPageCombo.currentText() == 'All':
                item_per_page = -1
            else:
                item_per_page = int(self.itemsPerPageCombo.currentText())
        except:
            pass
        # self.dataTable.load_data(group_field_names=self.groupMenu.selectedFieldNames,
        #                          sort_field_name=self.sortMenu.selectedFieldNames,
        #                          page_number=page,
        #                          items_per_page=item_per_page)
        # self.dataTable.refresh()
        # print 'refresh:', self.sortMenu.selectedFieldNames
        self.dataTable.load_and_refresh(group_field_names=self.groupMenu.selectedFieldNames,
                                        sort_field_names=self.sortMenu.selectedFieldNames,
                                        page_number=page,
                                        items_per_page=item_per_page)

    def next_page_clicked(self):
        current_page = int(self.currentPageEdit.text())
        if current_page + 1 <= self.allPageNum:
            self.currentPageEdit.setText(str(current_page + 1))
            self.refresh()

    def pre_page_clicked(self):
        current_page = int(self.currentPageEdit.text())
        if current_page - 1 >= 1:
            self.currentPageEdit.setText(str(current_page - 1))
            self.refresh()

    def current_page_edit(self):
        if self.dataTable.currentPageNumber != int(self.currentPageEdit.text()):
            self.refresh()

    def item_per_page_changed(self):
        # print self.itemsPerPageCombo.currentText()
        self.refresh()

    def resizeEvent(self, QResizeEvent):
        super(DataWidget, self).resizeEvent(QResizeEvent)
        self.loadingLabel.setFixedSize(self.size())


