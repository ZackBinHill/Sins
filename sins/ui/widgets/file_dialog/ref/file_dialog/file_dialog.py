# -*- coding: utf-8 -*-

import sys
import os
import re

from BQt import QtCore, QtWidgets, uic, QtGui
from bfx.ui import get_icon
from bfx_resources.icons import ICON_DIR
from bfx_resources import icons
from bfx.util.path import get_sequences
from bfx.pipeline.taskstarter.constants import ENV
from bfx.data.ple.task_context import TaskContext
from bfx.env.path.core import get_path

from bfx.util.log import bfx_get_logger

logger = bfx_get_logger(__name__)
logger.debug("loading module {0} at {1}".format(__name__, __file__))

FILTER_PATTERN = r"[ (](\*\.\w+)"


def size(bytes):
    # According to the Si standard KB is 1000 bytes, KiB is 1024
    # but on windows sizes are calculated by dividing by 1024 so we do what they do.
    kb = 1024.0
    mb = 1024.0 * kb
    gb = 1024.0 * mb
    tb = 1024.0 * gb
    if bytes >= tb:
        return "{0} TB".format(QtCore.QLocale().toString(bytes / tb, 'f', 3))
    if bytes >= gb:
        return "{0} GB".format(QtCore.QLocale().toString(bytes / gb, 'f', 2))
    if bytes >= mb:
        return "{0} MB".format(QtCore.QLocale().toString(bytes / mb, 'f', 1))
    if bytes >= kb:
        return "{0} KB".format(QtCore.QLocale().toString(bytes / kb, 'f', 1))
    return "{0} bytes".format(QtCore.QLocale().toString(bytes))


class FileItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, file_info=None, icon=None, typ=None, parent=None):
        super(FileItem, self).__init__(parent)

        self._file_info = file_info
        self._file_type = typ
        self._icon = icon

        self.setText(0, file_info.fileName())
        if file_info.isFile():
            self.setText(1, size((file_info.size())))
        if typ:
            self.setText(2, typ)
        self.setText(3, file_info.lastModified().toString(QtCore.Qt.SystemLocaleShortDate))

        self.setTextAlignment(1, QtCore.Qt.AlignRight)
        self.setIcon(0, icon)

    @property
    def file_name(self):
        return self._file_info.fileName()

    @property
    def file_path(self):
        return self._file_info.filePath()

    @property
    def is_dir(self):
        return self._file_info.isDir()


class SeqFilesItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, seq_data, parent=None):
        super(SeqFilesItem, self).__init__(parent)

        self._seq_data = seq_data
        self._file_info = QtCore.QFileInfo(self._seq_data["files"][0])
        self.path = self._seq_data["filename"]
        self._icon = QtWidgets.QFileIconProvider().icon(self._file_info)

        self.setText(0, "{name} {first}-{last}".format(name=os.path.basename(self.path),
                                                       first=self._seq_data["first_frame"],
                                                       last=self._seq_data["last_frame"]))
        self.setText(1, "")
        self.setText(2, "Sequence")
        self.setText(3, "")
        self.setIcon(0, self._icon)

    @property
    def file_name(self):
        return os.path.basename(self.file_path)

    @property
    def file_path(self):
        return self._seq_data["filename"]

    @property
    def is_dir(self):
        return False


class FileDialog(QtWidgets.QDialog):

    Detail = 0
    List = 1
    Accepted = 1
    Rejected = 0
    ExistingFile = 0
    ExistingFiles = 1
    FilesAndDirectories = 2

    def __init__(self, parent=None, caption="", directory="", filter="", task_context=""):
        """
        Constructs a file dialog with the given parent and caption that initially
        displays the contents of the specified directory.
        The contents of the directory are filtered before being shown in the dialog,
        using a semicolon-separated list of filters specified by each_filter.

        If you want to use multiple filters, separate each one with two semicolons. For example:

        "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"

        :param parent:
        :param caption:
        :param directory:
        :param filter:
        :param task_context:
        """
        super(FileDialog, self).__init__(parent=parent)

        # setup UI -------------------------------------------- #
        ui_file = os.path.join(os.path.dirname(__file__), 'design', 'file_dialog.ui')
        uic.loadUi(ui_file, self)
        self.view_mode_btns = QtWidgets.QButtonGroup()

        self._model = QtWidgets.QFileSystemModel()
        self.task_context = task_context

        self.tree_widget.resizeEvent = self._tree_resize_event
        # self.list_view.mouseReleaseEvent = self._list_view_mouse_release_event
        self.list_view.setModel(self.tree_widget.model())

        self.file_mode = self.FilesAndDirectories

        self.create_connect()
        self.init_ui(caption, directory, filter)

    def init_ui(self, caption="", directory="", filter=""):
        up_icon = os.path.join(ICON_DIR, "navigation", "svg", "ic_arrow_upward_48px.svg")
        self.go_up_btn.setIcon(get_icon(up_icon))
        list_icon = os.path.join(ICON_DIR, "action", "svg", "ic_view_module_48px.svg")
        self.list_radio.setIcon(get_icon(list_icon))
        detail_icon = os.path.join(ICON_DIR, "action", "svg", "ic_view_list_48px.svg")
        self.detail_radio.setIcon(get_icon(detail_icon))

        self.view_mode_btns.addButton(self.list_radio, self.List)
        self.view_mode_btns.addButton(self.detail_radio, self.Detail)
        self.detail_radio.click()

        self.go_to(QtCore.QDir.currentPath())
        self.sequences_ckb.setChecked(True)

        self.horizontalLayout_5.removeItem(self.main_view_hbox)
        self.horizontalLayout_5.removeWidget(self.side_bar)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.side_bar)
        main_view_widget = QtWidgets.QWidget()
        main_view_widget.setContentsMargins(0, 0, 0, 0)
        self.main_view_hbox.setContentsMargins(0, 0, 0, 0)
        main_view_widget.setLayout(self.main_view_hbox)
        self.splitter.addWidget(main_view_widget)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 5)
        self.horizontalLayout_5.addWidget(self.splitter)

        if caption:
            self.setWindowTitle(caption)

        if directory and os.path.isdir(directory):
            self.setDirectory(directory)

        if filter:
            self.setNameFilters(filter)
        else:
            self.files_type_cbbox.addItem("all files (*.*)")

        self.init_sidebar()

    def init_sidebar(self):
        self.setSidebarPath('Home', QtCore.QDir.homePath())
        self.setSidebarPath('Root', QtCore.QDir.rootPath())
        try:
            desktop_path = str(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DesktopLocation))
            desktop_path = unicode(desktop_path, 'utf-8')
            desktop_name = os.path.basename(desktop_path)
            if os.path.exists(desktop_path):
                self.setSidebarPath(desktop_name, desktop_path)
        except UnicodeEncodeError:
            pass
        except AttributeError:
            pass

        task_context = None
        if not self.task_context and os.getenv(ENV.entity_id, None):
            task_context = TaskContext.from_env()
        elif self.task_context:
            task_context = self.task_context

        if task_context:
            entity = task_context.entity
            show_name = entity.get_root().name
            show_path = os.path.join('/show', show_name)
            if os.path.exists(show_path):
                self.setSidebarPath(show_name, show_path)
            self.setSidebarPath('Publish', task_context.get_preview_dir(create=False))
            self.setSidebarPath('Workspace', task_context.get_workspace_dir(create=False))

    def create_connect(self):
        self.tree_widget.itemDoubleClicked.connect(self._tree_widget_item_double_clicked)
        self.tree_widget.itemClicked.connect(self._tree_widget_item_clicked)
        self.list_view.doubleClicked.connect(self._list_view_item_double_clicked)
        self.list_view.clicked.connect(self._list_view_item_clicked)
        self._model.layoutChanged.connect(self._model_layout_changed)
        self.go_up_btn.clicked.connect(self._go_up_btn_clicked)
        self.sequences_ckb.stateChanged.connect(self._sequences_ckb_clicked)
        self.dialog_btnbox.accepted.connect(self.accept)
        self.dialog_btnbox.rejected.connect(self.reject)
        self.path_nav_cbbox.editTextChanged.connect(self._path_nav_cbbox_exit_text_changed)
        self.files_type_cbbox.currentIndexChanged.connect(self._files_type_cbbox_changed)
        self.view_mode_btns.buttonClicked.connect(self._view_mode_btns_clicked)
        self.side_bar.itemPressed.connect(self._path_item_clicked)

    def create_path_item(self, text, path):
        item = QtWidgets.QListWidgetItem()
        item.setText(text)
        item.setIcon(get_icon(icons.FOLDER_BLACK))
        item.path_data = path  # May be dangerous.
        return item

    def selectedFiles(self):
        """
        Returns a list of strings containing the absolute paths of the selected files in the dialog.

        :return: list of strings
        """
        return self.selected_files

    @property
    def selected_files(self):
        """
        Returns a list of strings containing the absolute paths of the selected files in the dialog.

        :return: list of strings
        """

        if self.list_radio.isChecked():
            return [str(self.tree_widget.itemFromIndex(index).file_path) for index in self.list_view.selectedIndexes()]
        elif self.detail_radio.isChecked():
            return [str(item.file_path) for item in self.tree_widget.selectedItems()]

    @property
    def selected_filter(self):
        return str(self.files_type_cbbox.currentText())

    @classmethod
    def getOpenFileName(cls, parent=None, caption="", directory="", filter=""):
        """
        A class method you can use directly, more like the default one in original PyQt.
        Grab just one single file at one time.

        :return: selected files
        """
        tmp_file_dialog = cls(parent, caption, directory, filter)
        tmp_file_dialog.setFileMode(tmp_file_dialog.ExistingFile)
        result = tmp_file_dialog.exec_()
        if result == tmp_file_dialog.Accepted:
            return tmp_file_dialog.selected_files[0]

    @classmethod
    def getOpenFileNames(cls, parent=None, caption="", directory="", filter=""):
        """
        A class method you can use directly, more like the default one in original PyQt.

        :return: selected files
        """
        tmp_file_dialog = cls(parent, caption, directory, filter)
        tmp_file_dialog.setFileMode(tmp_file_dialog.ExistingFiles)
        result = tmp_file_dialog.exec_()
        if result == tmp_file_dialog.Accepted:
            return tmp_file_dialog.selected_files

    @classmethod
    def getOpenFileNamesAndDirectories(cls, parent=None, caption="", directory="", filter=""):
        tmp_file_dialog = cls(parent, caption, directory, filter)
        tmp_file_dialog.setFileMode(tmp_file_dialog.FilesAndDirectories)
        result = tmp_file_dialog.exec_()
        if result == tmp_file_dialog.Accepted:
            return tmp_file_dialog.selected_files

    @classmethod
    def getOpenFileNameAndFilter(cls, parent=None, caption="", directory="", filter=""):
        """
        A class method you can use directly, more like the default one in original PyQt.

        :return: [selected_files, selected_filter]
        """
        tmp_file_dialog = cls(parent, caption, directory, filter)
        tmp_file_dialog.setFileMode(tmp_file_dialog.ExistingFile)
        result = tmp_file_dialog.exec_()
        if result == tmp_file_dialog.Accepted:
            return [tmp_file_dialog.selected_files[0], tmp_file_dialog.selected_filter]

    @classmethod
    def getOpenFileNamesAndFilter(cls, parent=None, caption="", directory="", filter=""):
        """
        A class method you can use directly, more like the default one in original PyQt.

        :return: [selected_files, selected_filter]
        """
        tmp_file_dialog = cls(parent, caption, directory, filter)
        result = tmp_file_dialog.exec_()
        if result == tmp_file_dialog.Accepted:
            return [tmp_file_dialog.selected_files, tmp_file_dialog.selected_filter]

    def setSidebarPath(self, item_name, path):
        """
        :param item_name: Sidebar item name
        :param path: Path stored in the item
        """
        self.side_bar.addItem(self.create_path_item(item_name, path))

    def setSidebarPaths(self, path_list):
        for path in path_list:
            if os.path.isdir(path):
                path = os.path.abspath(path)
                self.setSidebarPath(os.path.basename(path), path)

    def setDirectory(self, path):
        """
        Sets the file dialog's current directory.

        :param str or QDir path:
        :return:
        """
        self.go_to(path)

    def setNameFilter(self, filter):
        """
        Sets the each_filter used in the file dialog to the given each_filter.

        If each_filter contains a pair of parentheses containing one or more of anything*something, separated by spaces,
        then only the text contained in the parentheses is used as the each_filter.
        This means that these calls are all equivalent:

        dialog.setNameFilter("All C++ files (*.cpp *.cc *.C *.cxx *.c++)")
        dialog.setNameFilter("*.cpp *.cc *.C *.cxx *.c++")

        :param str filter: a pair of parentheses containing one or more of anything*something, separated by spaces
        """
        self.setNameFilters(filter)

    def setNameFilters(self, filters):
        """
        Sets the filters used in the file dialog.

        :param list or str filters:
               ["Image files (*.png *.xpm *.jpg)", "Text files (*.txt)"] or
               string "Images (*.png *.xpm *.jpg);;Text files (*.txt)", separate each one with two semicolons.
        """
        if isinstance(filters, basestring):
            # "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
            items = filters.split(";;")
        elif isinstance(filters, (list, tuple)):
            items = filters

        self.files_type_cbbox.addItems(items)
        self._set_model_name_filters_from_file_type_cbbox()

    def setViewMode(self, mode):
        if mode == self.List:
            self.tree_widget.hide()
            self.list_view.show()
            self.list_radio.setChecked(True)
        elif mode == self.Detail:
            self.list_view.hide()
            self.tree_widget.show()
            self.detail_radio.setChecked(True)

    def setFileMode(self, mode):
        if mode not in [self.ExistingFile, self.ExistingFiles, self.FilesAndDirectories]:
            self.setFileMode(self.ExistingFile)
        else:
            self.file_mode = mode
            if mode == self.ExistingFile:
                self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
                self.tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            if mode == self.ExistingFiles or mode == self.FilesAndDirectories:
                self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
                self.tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def go_to(self, path):
        if isinstance(path, QtCore.QDir):
            path = path.path()
        self._model.setRootPath(path)
        self.path_nav_cbbox.setEditText(path)
        
    def mousePressEvent(self, QMouseEvent):
        if self.focusWidget() == self.list_view:
            if not self.selectedFiles():
                self.clear_filename_edit()
                return

        super(FileDialog, self).mousePressEvent(QMouseEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        super(FileDialog, self).mouseDoubleClickEvent(QMouseEvent)

    def _tree_widget_item_double_clicked(self, item, col):
        if item.is_dir:
            self.go_to(item.file_path)
        else:
            self.accept()

    def _tree_widget_item_clicked(self):
        self.filename_edit.setText(' '.join(map(lambda x: '"' + x + '"',
                                                [os.path.basename(_file) for _file in self.selectedFiles()])))

    def _list_view_item_double_clicked(self):
        path = self.selectedFiles()[0]
        if os.path.isdir(path):
            self.go_to(path)
        else:
            self.accept()

    def _list_view_item_clicked(self):
        self.filename_edit.setText(' '.join(map(lambda x: '"' + x + '"',
                                                [os.path.basename(_file) for _file in self.selectedFiles()])))

    def clear_filename_edit(self):
        self.filename_edit.clear()

    def _path_item_clicked(self, item):
        self.go_to(item.path_data)

    def _path_nav_cbbox_exit_text_changed(self, text):
        if os.path.isdir(str(text)):
            self.go_to(text)

    def _go_up_btn_clicked(self):
        up_path = os.path.dirname(str(self.path_nav_cbbox.currentText()))
        self.go_to(up_path)

    def _view_mode_btns_clicked(self, btn):
        mode = self.view_mode_btns.id(btn)
        self.setViewMode(mode)

    def _model_layout_changed(self):
        """load items from current root path of FileSystemModel into tree widget """
        self.tree_widget.clear()

        root_index = self._model.index(self._model.rootPath())
        for row in range(self._model.rowCount(root_index)):
            index = self._model.index(row, 0, root_index)
            file_item = FileItem(self._model.fileInfo(index),
                                 icon=self._model.fileIcon(index),
                                 typ=self._model.type(index),
                                 parent=self.tree_widget)
            self.tree_widget.addTopLevelItem(file_item)

        self.tree_widget.setColumnWidth(1, 80)
        self.tree_widget.setColumnWidth(2, 80)
        self.tree_widget.setColumnWidth(3, 140)

        if self.sequences_ckb.isChecked():
            self._collapse_to_sequences()

    def _sequences_ckb_clicked(self):
        if self.sequences_ckb.isChecked():
            self._collapse_to_sequences()
        else:
            self._model_layout_changed()
    
    def _files_type_cbbox_changed(self):
        self._set_model_name_filters_from_file_type_cbbox()
        
    def _collapse_to_sequences(self):
        sequences = get_sequences(str(self.path_nav_cbbox.currentText()))

        founded_seqs = {}

        for index in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(index)
            for seq in sequences:
                if item.file_path in seq["files"]:
                    self.tree_widget.setItemHidden(item, True)
                    self.list_view.setRowHidden(index, True)
                    if seq["filename"] not in founded_seqs:
                        founded_seqs[seq["filename"]] = {"row": index, "data": seq}

        for seq in founded_seqs:
            row = founded_seqs[seq]["row"]
            data = founded_seqs[seq]["data"]
            self.tree_widget.insertTopLevelItem(row, SeqFilesItem(data))

    def _set_model_name_filters_from_file_type_cbbox(self):
        filter_str = str(self.files_type_cbbox.currentText())

        filters = re.findall(FILTER_PATTERN, filter_str.strip())
        filters = list(set(filters))
        if not filters:
            self._model.setNameFilterDisables(True)
        else:
            self._model.setNameFilters(filters)
            self._model.setNameFilterDisables(False)

    def accept(self):
        if self.focusWidget() == self.path_nav_cbbox:
            pass
        else:
            files = self.selectedFiles()
            if not files:
                return
            else:
                if self.file_mode == self.ExistingFile:
                    current_file = files[0]
                    if os.path.isdir(current_file):
                        self.go_to(current_file)
                        return
                elif self.file_mode == self.ExistingFiles:
                    if len(files) == 1:
                        if os.path.isdir(files[0]):
                            self.go_to(files[0])
                            return
                    else:
                        single_directory = None
                        for path in files:
                            if os.path.isdir(path):
                                if single_directory:
                                    QtWidgets.QMessageBox.about(self, 'About',
                                                                'What you select containing 2 or more directories')
                                    return
                                else:
                                    single_directory = path
                        else:
                            if single_directory:
                                self.go_to(single_directory)
                                return
                elif self.file_mode == self.FilesAndDirectories:
                    pass

            super(FileDialog, self).accept()

    def reject(self):
        super(FileDialog, self).reject()

    def _tree_resize_event(self, event):
        new_width = event.size()
        extra_cols_width = 0

        for col in range(self.tree_widget.columnCount()):
            if col > 0:
                extra_cols_width += self.tree_widget.columnWidth(col)

        self.tree_widget.setColumnWidth(0, new_width.width()-extra_cols_width-20)


def main():
    """main function that's render when the script is render as a standalone script."""

    app = QtWidgets.QApplication(sys.argv)
    os.environ[ENV.entity_id] = str(315715)
    os.environ[ENV.task_path] = 'test_guzy'

    dialog = FileDialog()
    # dialog.setDirectory("/show/CWT/seq/sc002/shot/sc002_0050/task/plate/workspace/BP/sc002_0050_plate_bp_v001/output/exr/2048x1152")
    # dialog.setNameFilter("Images (*.png *.exr *.jpg);;Text files (*.txt);;XML files (*.xml)")
    # dialog.setSidebarPaths(['/sw/PLE/workspace/guzy/', '/sw/PLE/workspace/chencheng/'])
    dialog.setViewMode(FileDialog.List)
    result = dialog.exec_()
    if result == FileDialog.Accepted:
        print dialog.selected_files

    # sys.exit(app.exec_())


if __name__ == '__main__':
    main()

