import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

PROJECT_ROOT = os.path.dirname(__file__)
PROJECT_NAME = os.path.split(PROJECT_ROOT)[-1]

try:
    SECRET_KEY
except NameError:
    SECRET_FILE = os.path.join(PROJECT_ROOT, 'secret.txt')
    try:
        SECRET_KEY = open(SECRET_FILE).read().strip()
    except IOError:
        try:
            from random import choice
            SECRET_KEY = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
            secret = file(SECRET_FILE, 'w')
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            Exception('Please create a %s file with random characters to generate your secret key!' % SECRET_FILE)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('admin', 'webmaster@rdev.info'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'local_database.db'),
    }
}

TIME_ZONE = 'Europe/Berlin'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = PROJECT_ROOT+'/media/'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

DEFAULT_FROM_EMAIL = 'webmaster@rdev.info'
SERVER_EMAIL = 'webmaster@rdev.info'
EMAIL_SUBJECT_PREFIX = '[%s] ' % PROJECT_NAME

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

ROOT_URLCONF = '%s.urls' % PROJECT_NAME

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'pagination',
    'djcelery',
    'formwizard',
    'ghettoq',
    'south',
    'journeyman.projects',
    'journeyman.workers',
    'journeyman.builds',
)

import djcelery
djcelery.setup_loader()

CARROT_BACKEND = 'ghettoq.taproot.Database'
CELERY_RESULT_BACKEND = 'database'
CELERY_DEFAULT_EXCHANGE = "tasks"
CELERY_DEFAULT_QUEUE = 'tasks'
CELERY_QUEUES = {
    'tasks': {'exchange': 'tasks'},
}

try:
    from local_settings import *
except ImportError:
    pass
