"""
Django settings for project project.
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '123'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',

    'djutils',
    'bootstrap4',

    'background_tasks',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.login_required.LoginRequiredMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'background_tasks.context_processors.user_background_tasks',
                'core.context_processors.base_templates',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_L10N = False
USE_TZ = False

DATE_INPUT_FORMATS = ['%d.%m.%Y', '%Y-%m-%d', ]
DATE_FORMAT = 'd.m.Y'
DATETIME_FORMAT = 'd.m.Y H:i'
SHORT_DATETIME_FORMAT = 'd.m.Y H:i'

DIR_FOR_TMP_FILES = '/tmp/med-org-portal/'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_WORKER_PREFETCH_MULTIPLIER = 1


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


LOGIN_REQUIRED_URLS_EXCEPTIONS = (
    r'/static/',
    r'/node_modules/',
    r'/login(.*)$',
    r'/logout(.*)$',
)

MIS_URL = ''
MIS_TOKEN = ''

TEMPLATES_DICT = {
    "base": 'core/base.html',
    "index": 'core/index.html',
    "workers_done_report": 'core/reports/workers_done.html',
    "direction_list": 'core/directions/list.html',
}

# время действия направления (в днях)
# если не указано, то направление действует до конца текущего года
DIRECTION_ACTION_DAYS = os.environ.get('DIRECTION_ACTION_DAYS', '')

try:
    from project.local_settings import *
except ImportError:
    print("Warning: no local_settings.py")

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'kakanikita2001@gmail.com'
EMAIL_HOST_PASSWORD = '763420asd1'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



