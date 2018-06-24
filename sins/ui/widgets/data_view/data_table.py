# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/7/2018

from sins.utils.log import log_cost_time
from sins.config.data_view_configs import *
from sins.config.utils import DataItem, DataGroup, get_prefetch_models
from sins.ui.widgets.action import SeparatorAction
from sins.ui.widgets.label import QLabelButton
from sins.db.models import *
from sins.db.permission import is_editable
import sys
import copy
import math


logger = get_logger(__name__)

EDITLABEL_SIZE = 20
FOREIGN_POPULATE_DEPTH = 2

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
            for index, field in enumerate(config.first_fields()):
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

            # print query[0].sequence.name
            # print query.sql()

            # -------- old --------
            # if len(self.currentGroups) > 0:
            #     base_group_field_name = self.currentGroups[0]['field_name']
            #     reverse = self.currentGroups[0]['reverse']
            #     base_group_field = self.config.find_field(base_group_field_name)
            # else:
            #     base_group_field = None
            # if base_group_field is not None:
            #     parent_configs = base_group_field.parent_configs
            #     if len(parent_configs) <= 1:
            #         # print self.db_model, base_group_field.name
            #         group_attr = base_group_field.group_attr
            #         if isinstance(group_attr, str):
            #             if reverse:
            #                 query = query.order_by(getattr(self.db_model, group_attr).desc())
            #             else:
            #                 query = query.order_by(getattr(self.db_model, group_attr))
            #         elif isinstance(group_attr, list):
            #             for model in group_attr[:-1]:
            #                 query = query.join(model)
            #             if reverse:
            #                 query = query.order_by(getattr(group_attr[-2], group_attr[-1]).desc())
            #             else:
            #                 query = query.order_by(getattr(group_attr[-2], group_attr[-1]))
            #     else:
            #         current_config = self.config
            #         for config_name in parent_configs[1:]:
            #             out_field = current_config.find_out_field(config_name)
            #             current_config = out_field.config
            #             # print current_config.db_model
            #             query = query.join(current_config.db_model)
            #         # print current_config.db_model, base_group_field.name
            #         query = query.order_by(getattr(current_config.db_model, base_group_field.group_attr))
            # #

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

    # @log_cost_time
    # def set_item_widget(self):
    #     num = len(self.tempItemWidgets)
    #     for index, i in enumerate(self.tempItemWidgets):
    #         self.setItemWidget(i[0], i[1], i[2])
    #         if index % 100 == 0:
    #             QApplication.processEvents()
    #         # print i[2].parent().parent()
    #     for i in range(self.columnCount()):
    #         self.section_resized(i)
    #     self.updateGeometries()
    #     self.tempItemWidgets = []
    #
    # @log_cost_time
    # def add_temp_item_field(self):
    #     for index, i in enumerate(self.tempItemFields):
    #         self.add_field(i[0], i[1], i[2], i[3])
    #         if index % 100 == 0:
    #             QApplication.processEvents()
    #     self.tempItemFields = []

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

        cellWidgetName = field.inner_widget
        # editable = True if current_permission in field.edit_permission else False
        # editable = is_editable(field, data, field_name)
        cellWidget = cellWidgetName(treeitem=item,
                                    column=index,
                                    model_attr=field.model_attr,
                                    column_label=field.label,
                                    parent=self,
                                    **field.widget_attr_map)
        # print 'add field:', cellWidget, child.data[field.name]

        if field_name in data.keys():
            cellWidget.set_value(data[field_name]['value'])
            cellWidget.set_db_instance(data[field_name]['db_instance'])
            cellWidget.set_read_only(is_editable(editable_permission=field.edit_permission,
                                                 db_instance=data[field_name]['db_instance']))
        if not field.readonly:
            cellWidget.add_front()
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


# class TestTree(QTreeWidget):
#     def __init__(self, parent=None):
#         super(TestTree, self).__init__(parent)
#
#         self.setColumnCount(10)
#         self.setSelectionMode(QAbstractItemView.ExtendedSelection)
#
#         self.dataItems = []
#
#         # self.init_ui()
#
#         self.itemSelectionChanged.connect(self.item_select_changed)
#
#     def init_ui(self):
#         root = QTreeWidgetItem()
#         self.addTopLevelItem(root)
#         self.setFirstItemColumnSpanned(root, True)
#
#         root1 = QTreeWidgetItem()
#         root.addChild(root1)
#         self.setFirstItemColumnSpanned(root1, True)
#
#         for i in range(1):
#             item = QTreeWidgetItem()
#             root1.addChild(item)
#
#             # cellLineEdit = CellLineEdit(text="aaddddddddddda", editable=True, treeitem=item, parent=self)
#             # cellLineEdit.add_front()
#             # # cellLineEdit.resizesignal.connect(self.resize_column)
#             #
#             # cellTextEdit1 = CellTextEdit(text="sdfs ss ss s s s s s s  s s s s s  s s s s ", editable=False,
#             #                                       treeitem=item, parent=self)
#             # cellTextEdit2 = CellTextEdit(text="sdfs ss ss s s s s s s  s s s s s  s s s s ", editable=False,
#             #                              treeitem=item, parent=self)
#             # # cellTextEdit.add_front()
#             # # cellTextEdit.resizesignal.connect(self.resize_column)
#             #
#             # cellStatusEdit = CellStatusEdit(editable=True,treeitem=item, parent=self)
#             # cellStatusEdit.add_front()
#             # # cellStatusEdit.resizesignal.connect(self.resize_column)
#
#             cellLinkLabel = CellLinkLabel(editable=True, treeitem=item, parent=self)
#             # cellLinkLabel.add_front()
#             # cellLinkLabel.resizesignal.connect(self.resize_column)
#
#             # self.setItemWidget(item, 0, cellLineEdit)
#             # self.setItemWidget(item, 1, cellStatusEdit)
#             # self.setItemWidget(item, 2, cellTextEdit1)
#             # self.setItemWidget(item, 4, cellTextEdit2)
#             self.setItemWidget(item, 3, cellLinkLabel)
#
#             item.setText(0, 'zxcv')
#             self.dataItems.append(item)
#
#         self.setColumnWidth(0, 150)
#         self.setColumnWidth(1, 100)
#         self.setColumnWidth(2, 200)
#
#         self.addTopLevelItem(QTreeWidgetItem(["aaa"]))
#
#         root.setExpanded(True)
#         root1.setExpanded(True)
#
#         self.set_style()
#
#         self.header().setSortIndicatorShown(True)
#         self.header().setSortIndicator(1, Qt.AscendingOrder)
#         # self.header().setSectionsClickable(True)
#         QtCompat.QHeaderView.setSectionsClickable(self.header(), True)
#         self.header().sectionClicked.connect(self.test2)
#         self.header().sectionResized.connect(self.section_resized)
#         # self.setUniformRowHeights(True)
#
#     def section_resized(self, index, oldsize, newsize):
#         # print index, oldsize, newsize
#         for item in self.dataItems:
#             if self.itemWidget(item, index).autoHeight == True:
#                 # print self.itemWidget(item, index).height()
#                 item.setSizeHint(index, QSize(newsize, self.itemWidget(item, index).height()))
#                 # self.updateEditorGeometries()
#                 # self.updateGeometries()
#                 # print item.sizeHint(index)
#                 modelindex = self.indexFromItem(item, index)
#                 # print modelindex, self.rowHeight(modelindex)
#                 # QTreeWidgetItem.sizeHint(0)
#                 newheight = 0
#                 for j in range(self.columnCount()):
#                     # newheight = max(self.itemWidget(item, index).height(), self.rowHeight(modelindex))
#                     temp = self.itemWidget(item, j)
#                     temph = temp.targetHeight if hasattr(temp, 'targetHeight') else 0
#                     print temph
#                     newheight = max(newheight, temph)
#
#                 print newheight
#                 for j in range(self.columnCount()):
#                     item.setSizeHint(j, QSize(newsize, newheight))
#
#     def test2(self, index):
#         print index
#         for item in self.dataItems:
#             height = item.sizeHint(0).height()
#             print height, item.sizeHint(0).height()
#             item.setSizeHint(0, QSize(100, height + 10))
#             print item.sizeHint(0)
#             # self.updateEditorGeometries()
#
#     def set_style(self):
#         style = """
#         *{
#             outline:0px
#         }
#         QTreeWidget::item{
#             border-right: 1px solid gray;
#             border-bottom: 1px solid gray;
#         }
#         QTreeWidget::item:selected{
#             background:rgb(200, 200, 255);
#         }
#         QTreeWidget::item:has-children{
#             background:rgb(150, 150, 150);
#         }
#         QTreeWidget::branch:!has-children:!selected:has-siblings:adjoins-item,
#         QTreeWidget::branch:!has-children:!selected:!has-siblings:adjoins-item{
#             image:url(%s/icon/unchecked.png);
#         }
#         QTreeWidget::branch:!has-children:selected:has-siblings:adjoins-item,
#         QTreeWidget::branch:!has-children:selected:!has-siblings:adjoins-item{
#             image:url(%s/icon/checked.png)
#         }
#         QTreeWidget::branch:has-children:selected:!has-siblings:adjoins-item{
#             image:url(%s/icon/checked.png)
#         }
#         """
#         self.setStyleSheet(style.replace("%s", resource.Res_Folder).replace("\\", "/"))
#
#     def resize_column(self, width, height):
#         if hasattr(self.sender(), "treeitem"):
#             treeitem = self.sender().treeitem
#             # print treeitem, treeitem.row()
#             treeitem.setSizeHint(0, QSize(width, height))
#             # QTreeWidgetItem.setSizeHint()
#             self.updateEditorGeometries()
#             self.updateGeometries()
#
#     def item_select_changed(self):
#         for item in self.selectedItems():
#             for index in range(item.childCount()):
#                 child = item.child(index)
#                 child.setSelected(True)
#
#
# class TestWidget(QWidget):
#     def __init__(self):
#         super(TestWidget, self).__init__()
#         self.tree = TestTree()
#         self.layout = QHBoxLayout()
#         self.layout.addWidget(self.tree)
#         self.setLayout(self.layout)


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


class LoadingLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(LoadingLabel, self).__init__(*args, **kwargs)

        self.loadingMovie = resource.get_qmovie('gif', 'loading1.gif')
        self.setMovie(self.loadingMovie)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('background:rgb(150, 150, 150, 100)')

    def set_loading(self, loading=True):
        if loading:
            self.setVisible(True)
            self.loadingMovie.start()
        else:
            self.setVisible(False)
            self.loadingMovie.stop()


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


class LoadThread(QThread):
    loadFinish = Signal()
    def __init__(self, tree):
        super(LoadThread, self).__init__()

        self.tree = tree

    def set_attr(self,
                 group_field_names=None,
                 sort_field_name=None,
                 page_number=None,
                 items_per_page=None):
        self.group_field_names = group_field_names
        self.sort_field_name = sort_field_name
        self.page_number = page_number
        self.items_per_page = items_per_page

    def run(self):
        self.tree.load_data(self.group_field_names,
                            self.sort_field_name,
                            self.page_number,
                            self.items_per_page,
                            )
        self.loadFinish.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    department_config = DepartmentConfig()
    permissionGroup_config = PermissionGroupConfig()
    person_config = PersonConfig()
    status_config = StatusConfig()
    project_config = ProjectConfig()
    group_config = GroupConfig()
    pipelineStep_config = PipelineStepConfig()
    sequence_config = SequenceConfig()
    assetType_config = AssetTypeConfig()
    tag_config = TagConfig()
    asset_config = AssetConfig()
    shot_config = ShotConfig()
    task_config = TaskConfig()

    # panel = TestWidget()
    panel = DataWidget()
    # panel = PersonTree()
    # panel = CellTextEdit()
    panel.show()
    panel.load_config(config=person_config)
    # panel.load_config(config=status_config)
    # panel.load_config(config=project_config)
    # panel.load_config(config=group_config)
    # panel.load_config(config=department_config)
    # panel.load_config(config=pipelineStep_config)
    # panel.load_config(config=sequence_config)
    # panel.load_config(config=assetType_config)
    # panel.load_config(config=tag_config)
    # panel.load_config(config=asset_config)
    # panel.load_config(config=shot_config)
    # panel.load_config(config=task_config)
    panel.refresh()
    app.exec_()