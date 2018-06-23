# -*- coding: utf-8 -*-

import sys
import time
import getpass
import os
# os.environ['BFX_LOG'] = 'debug'
# import webbrowser
from bfx.data.util.peewee import prefetch
from bfx.data.prod.shotgun.production2.models import *


person = Person.get(login='xinghuan')
print person

