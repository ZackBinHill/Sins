# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/6/2018

import os
from models import *
# from test.db_test05 import *
from sins.db import default_data
from sins.utils.path.file import get_file_mime
from sins.module import filetype
import magic
import mimetypes

# from sins.ui.widgets.table.data_table_configs import *
TEST_DATA_FOLDER = 'F:/Temp/pycharm/Sins_project/Sins/sins/db/test/test_data'

import time

t = time.time()

root = Person.get(user_login='postgres')
for p in root.projects:
    print p.code


print time.time() - t





























