# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 6/6/2018

from sins.db.models import *

# from sins.ui.widgets.table.data_table_configs import *
TEST_DATA_FOLDER = 'F:/Temp/pycharm/Sins_project/Sins/test/test_data'

import time

t = time.time()

test_movie04 = os.path.join(TEST_DATA_FOLDER, 'version', 'version04.jpg')
version = Version.get(id=100)
version.upload_file(test_movie04, field='uploaded_movie')


print time.time() - t





























