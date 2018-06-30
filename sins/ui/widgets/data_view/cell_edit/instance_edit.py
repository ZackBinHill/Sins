# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import *
from .basic import CellWidget
from .choose_edit import get_choose
from sins.ui.utils.screen import get_screen_size
from sins.ui.widgets.flow_layout import FlowLayout
from sins.db.models import *


OBJECT_ICON_SIZE = 17


class TextBrowser(QTextBrowser):
    def __init__(self, *args, **kwargs):
        super(TextBrowser, self).__init__(*args, **kwargs)

        self.setOpenLinks(False)
        self.setStyleSheet("""
        *{
        border:none;
        background:transparent;
        }
        """)

    def loadResource(self, type, name):
        # super(TextBrowser, self).loadResource(type, name)
        # print type, name
        return


class CellSingleObjectEdit(CellWidget):
    def __init__(self, **kwargs):
        super(CellSingleObjectEdit, self).__init__(**kwargs)

        self.label = QLabel('', self)
        self.label.setOpenExternalLinks(False)
        self.label.linkActivated.connect(self.open_new_page)
        # self.label = TextBrowser(self)

    def set_value(self, value):
        label = value['label']
        db_object = value['object']
        if db_object is not None:
            text = ''
            if hasattr(db_object, 'icon'):
                text += '<img src="{icon}" width={size} height={size}>'.format(
                    icon=db_object.icon,
                    size=OBJECT_ICON_SIZE
                )
            text += '<a href="{url}">{label}</a>'.format(
                url='test',
                label=label
            )
            if hasattr(db_object, 'status'):
                status = db_object.status
                loaded_status_list = get_class_from_name_data('sins.ui.widgets.data_view.cell_edit',
                                                              'loaded_{}_status'.
                                                              format(db_object.__class__.__name__.lower()))
                status_icon = get_choose(loaded_status_list, status).icon
                if status_icon is not None and os.path.exists(status_icon):
                    text += '<img src="{icon}" width={size} height={size}>'.format(
                        icon=status_icon,
                        size=OBJECT_ICON_SIZE
                    )
            # text += '<img src="{}">'.format(db_object.icon)
            # print text
            self.label.setText(text)

    def open_new_page(self, url):
        print 'open page:', url
        current_parent = self.parent()
        while current_parent.parent() is not None:
            current_parent = current_parent.parent()
        # print current_parent
        if hasattr(current_parent, 'to_page'):
            current_parent.to_page(url)
        # self.link.emit(url)


class RemoveLabelButton(QLabel):
    clicked = Signal()

    def __init__(self, parent=None):
        super(RemoveLabelButton, self).__init__(parent)
        self.setPixmap(resource.get_pixmap("button", "close_darkgray.png", scale=15))
        self.setFixedSize(15, 15)

    def mouseReleaseEvent(self, *args, **kwargs):
        self.clicked.emit()


class SingleObjectWidget(QWidget):
    def __init__(self, db_object, label_attr):
        super(SingleObjectWidget, self).__init__()

        self.db_object = db_object

        self.backLabel = QLabel(self)
        self.backLabel.setStyleSheet("""
        background: rgb(200, 200, 230);
        border-radius:13px
        """)
        self.objectLabel = QLabel(getattr(self.db_object, label_attr))
        self.removeButton = RemoveLabelButton(parent=self)
        self.masterLayout = QHBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignCenter)
        self.masterLayout.setContentsMargins(10, 5, 10, 5)
        self.masterLayout.addWidget(self.objectLabel)
        self.masterLayout.addWidget(self.removeButton)
        self.setLayout(self.masterLayout)

        self.setFixedHeight(26)

    def resizeEvent(self, *args, **kwargs):
        super(SingleObjectWidget, self).resizeEvent(*args, **kwargs)
        self.backLabel.setFixedSize(self.size())


class MultiObjectEditWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(MultiObjectEditWidget, self).__init__(*args, **kwargs)

        self.db_object_list = []
        self.init_ui()

    def init_ui(self):

        self.setWindowFlags(Qt.Popup)

        self.objectsWidget = QWidget()
        self.objectsLayout = FlowLayout(spacing=10, margin=10, parent=self.objectsWidget)
        self.objectsWidget.setLayout(self.objectsLayout)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.objectsWidget)
        self.scrollArea.setWidgetResizable(True)

        self.lineEdit = QLineEdit()

        self.buttonLayout = QHBoxLayout()
        self.applyButton = QPushButton('Apply')
        self.cancelButton = QPushButton('Cancel')
        self.buttonLayout.setAlignment(Qt.AlignRight)
        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.masterLayout = QVBoxLayout()
        self.masterLayout.addWidget(self.scrollArea)
        self.masterLayout.addWidget(self.lineEdit)
        self.masterLayout.addLayout(self.buttonLayout)
        self.setLayout(self.masterLayout)

        self.resize(400, 300)

        self.setStyleSheet("""
        QScrollArea, QLineEdit{
            border:none;
        }
        """)

        self.applyButton.clicked.connect(self.apply_clicked)
        self.cancelButton.clicked.connect(self.close)

    def set_value(self, db_objects_dict):
        db_objects = db_objects_dict['objects']
        label_attr = db_objects_dict['object_label_attr']
        if db_objects is None:
            db_objects = []
        print db_objects
        for db_object in db_objects:
            singleObjectWidget = SingleObjectWidget(db_object, label_attr)
            singleObjectWidget.removeButton.clicked.connect(self.remove_object)
            self.objectsLayout.addWidget(singleObjectWidget)
            self.db_object_list.append(db_object)

    def add_object(self):
        pass

    def remove_object(self):
        singleObjectWidget = self.sender().parent()
        db_object = singleObjectWidget.db_object
        index = self.db_object_list.index(db_object)
        print index
        singleObjectWidget.setParent(None)
        self.objectsLayout.removeWidget(singleObjectWidget)
        self.db_object_list.remove(db_object)

    def apply_clicked(self):
        self.close()


class CellMultiObjectEdit(CellWidget):
    def __init__(self, linkable=True, link_model=None, **kwargs):
        super(CellMultiObjectEdit, self).__init__(**kwargs)

        self.linkable = linkable
        self.link_model_name = link_model

        self.label = TextBrowser(self)
        self.label.anchorClicked.connect(self.open_new_page)

        self.edit_widget = None

    def set_value(self, value):
        self.data_value = value
        label_attr = value['object_label_attr']
        db_objects = value['objects']
        # print db_objects
        # if self.link_model_name == 'Project':
        #     self_projects = current_user_object.projects
        #     db_object_query = db_object_query.select().where(Project.id.in_(self_projects))
        if db_objects is not None:
            text = ''
            for db_object in db_objects:
                # print db_object
                if hasattr(db_object, 'icon'):
                    text += '<img src="{icon}" width={size} height={size}>'.format(
                        icon=db_object.icon,
                        size=OBJECT_ICON_SIZE
                    )
                if self.linkable:
                    text += '<a href="{url}"><font color=#404040>{label}</font></a>'.format(
                        url='test',
                        label=getattr(db_object, label_attr)
                    )
                else:
                    text += '<font color=#404040>{label}</font>'.format(
                        label=getattr(db_object, label_attr)
                    )
                if hasattr(db_object, 'status'):
                    status = db_object.status
                    loaded_status_list = get_class_from_name_data('sins.ui.widgets.data_view.cell_edit',
                                                                  'loaded_{}_status'.
                                                                  format(db_object.__class__.__name__.lower()))
                    status_icon = get_choose(loaded_status_list, status).icon
                    if status_icon is not None and os.path.exists(status_icon):
                        text += '<img src="{icon}" width={size} height={size}>'.format(
                            icon=status_icon,
                            size=OBJECT_ICON_SIZE
                        )
                text += ', '
            self.label.setText(text)

    def set_editable(self):
        if self.edit_widget is None:
            self.edit_widget = MultiObjectEditWidget(self.treeitem.tree)
        self.edit_widget.set_value(self.data_value)
        screen_size = get_screen_size()
        self.edit_widget.move((screen_size.width() - self.edit_widget.width()) / 2,
                            (screen_size.height() - self.edit_widget.height()) / 2)

        self.edit_widget.show()

    def open_new_page(self, url):
        print 'open page:', url
        current_parent = self.parent()
        while current_parent.parent() is not None:
            current_parent = current_parent.parent()
        # print current_parent
        if hasattr(current_parent, 'to_page'):
            current_parent.to_page(url)
        # self.link.emit(url)

