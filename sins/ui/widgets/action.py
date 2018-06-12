# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 5/17/2018
from sins.module.sqt import *


class SeparatorAction(QWidgetAction):
    def __init__(self, text='', *args, **kwargs):
        super(SeparatorAction, self).__init__(*args, **kwargs)

        label = QLabel(text, self.parent())
        label.setObjectName('Separator')
        self.setDefaultWidget(label)