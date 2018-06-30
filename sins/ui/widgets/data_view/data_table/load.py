# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/30/2018

from sins.module.sqt import *
from sins.utils.res import resource


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
