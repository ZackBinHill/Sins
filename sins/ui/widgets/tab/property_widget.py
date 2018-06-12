# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/21/2018

from sins.module.sqt import *
from sins.utils.surl.surl import SURL


class PropertyWidget(QWidget):
    def __init__(self, parent=None):
        super(PropertyWidget, self).__init__(parent)

        self.coreproperty_list = list()
        self.coreproperty_apply = False

        self._surl = SURL('sins://page')

    def set_core_property(self, **kwargs):
        self.coreproperty_apply = False
        for key in kwargs:
            if key in self.coreproperty_list:
                setattr(self, key, kwargs[key])
                self.coreproperty_apply = True

    @property
    def surl(self):
        return self._surl

    @surl.setter
    def surl(self, value):
        # print value
        if isinstance(value, list):
            self._surl = SURL.page_to_url(value)
        elif isinstance(value, SURL):
            # print value.url
            self._surl = value
        print 'current url:', self._surl.url


# class LinkObject(QObject):
#     link = Signal(str)
#     link_objects = list()
#
#     def add_link_object(self, object):
#         # self.link_objects = []
#         self.link_objects.append(object)
#
#     def create_link_signal(self):
#         # print self.__class__, 'create link'
#         # print self.link_objects
#         for obj in self.link_objects:
#             obj.link.connect(self.emit_link)
#
#     def emit_link(self, link_str):
#         # print self.__class__, 'emit link', link_str
#         self.link.emit(link_str)

