import os
SETTINGS_DIR = os.path.dirname(__file__)
REPO_DIR = os.path.join(
    os.path.abspath(
        os.path.join(SETTINGS_DIR, os.path.pardir),
    ),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'archive',
    'cumulus',
    'greeking',
    'robots',
    'taggit',
    'tastypie',
    'toolbox',
    'memento',
    'django_celery_results',
)

ALLOWED_HOSTS = [
    'www.pastpages.org',
    'pastpages.org',
    'localhost',
]

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Localization
ADMINS = (
    ('Ben Welsh', 'ben.welsh@gmail.com'),
)
MANAGERS = ADMINS
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static and media files
MEDIA_ROOT = os.path.join(SETTINGS_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(SETTINGS_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(SETTINGS_DIR, 'templates', 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "toolbox.context_processors.site",
            ],
        },
    },
]

MUNIN_ROOT = '/var/cache/munin/www/'

# Request handling
MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
WSGI_APPLICATION = 'project.wsgi.application'

# Extras
SITE_ID = 1
ROOT_URLCONF = 'project.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(SETTINGS_DIR, 'django.log'),
            'maxBytes': 1024 * 1024 * 5, # 5MB,
            'backupCount': 0,
            'formatter': 'verbose'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s|%(asctime)s|%(module)s|%(process)d|%(thread)d|%(message)s',
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s|%(message)s'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'archive': {
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'bakery': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'toolbox': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# Cache
CACHE_MIDDLEWARE_SECONDS = 60 * 5
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_KEY_PREFIX  = ''
DJANGO_MEMCACHED_REQUIRE_STAFF = True

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_BACKEND = 'django-db'

try:
    from settings_dev import *
except ImportError:
    from settings_prod import *
