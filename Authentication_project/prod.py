from __future__ import absolute_import, unicode_literals
import os
from .settings import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ['*']

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600),
}

# EMAIL_HOST_USER = ''
# EMAIL_HOST = ''
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_PASSWORD = ''
