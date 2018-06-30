# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.ui.widgets.label import ThumbnailLabel
from sins.ui.widgets.image_upload_edit import ImageUploadEdit
from sins.ui.utils.screen import get_screen_size
from .basic import CellWidget


# thumbnail
class CellThumbnail(CellWidget):
    def __init__(self, **kwargs):
        super(CellThumbnail, self).__init__(**kwargs)

        self.autoHeight = True
        self.auto_resize = True
        self.update_geo = False

        self.thumbnailPath = ''
        self.thumbnailLabel = ThumbnailLabel(dynamic=False,
                                             background='transparent',
                                             parent=self)
        self.thumbnailLabel.cacheDone.connect(self.load_done)

        self.thumbnailEdit = None

    def set_value(self, value):
        if value is not None:
            self.data_value = value
            self.update_label()

    def update_label(self):
        self.thumbnailPath = self.data_value.host_path
        if self.thumbnailPath.endswith('.png'):
            self.thumbnailLabel.use_opencv = False
        else:
            self.thumbnailLabel.use_opencv = True
        self.thumbnailLabel.create_preview(self.thumbnailPath)

    def set_editable(self):
        if self.thumbnailEdit is None:
            self.thumbnailEdit = ImageUploadEdit(parent=self)
            self.thumbnailEdit.applyClicked.connect(self.upload_thumbnail)
        self.thumbnailEdit.show()
        screen_size = get_screen_size()
        self.thumbnailEdit.move((screen_size.width() - self.thumbnailEdit.width()) / 2,
                              (screen_size.height() - self.thumbnailEdit.height()) / 2)

        # print self.data_value
        if self.data_value is not None:
            self.thumbnailEdit.set_image(self.data_value.host_path)
        else:
            pass

    def upload_thumbnail(self):
        if self.thumbnailEdit.current_image is not None:
            uploaded_file = self.db_instance.upload_file(file_path=self.thumbnailEdit.current_image,
                                         description='upload new thumbnail')
            self.data_value = uploaded_file
            self.update_geo = True
            self.update_label()

    def load_done(self):
        self.set_size()
        # print 'load done'
        if self.treeitem is not None:
            self.treeitem.tree.section_resized(index=self.column)
            if self.update_geo:
                self.treeitem.tree.updateGeometries()
        self.update_geo = False

    def resizeEvent(self, *args, **kwargs):
        super(CellThumbnail, self).resizeEvent(*args, **kwargs)
        self.set_size()

    def set_size(self):
        self.thumbnailLabel.setFixedWidth(self.width())
        self.thumbnailLabel.set_resize_size()
        targetHeight = self.thumbnailLabel.targetHeight
        if self.auto_resize:
            if targetHeight == 0:
                targetHeight = 20
        else:
            targetHeight = self.height()
        self.thumbnailLabel.setFixedHeight(targetHeight)
        self.setFixedHeight(targetHeight)
        self.targetHeight = targetHeight

