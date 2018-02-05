from __future__ import absolute_import, unicode_literals
import os
from .settings import *
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = ['*','.softscores.com']


STATIC_ROOT = os.path.join(BASE_DIR, 'static')


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600),
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER = 'softscoresapp@gmail.com'
EMAIL_HOST_PASSWORD = 'SoftScoresAppTelAviv'
DEFAULT_EMAIL_FROM = 'softscoresapp@gmail.com'
EMAIL_USE_TLS = True
