from __future__ import absolute_import, unicode_literals
import os
from .settings import *

if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
