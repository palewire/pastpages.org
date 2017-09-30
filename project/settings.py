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
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    os.path.join(SETTINGS_DIR, 'templates'),
)
MUNIN_ROOT = '/var/cache/munin/www/'

# Request handling
MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'toolbox.middleware.domains.DomainRedirectMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
WSGI_APPLICATION = 'project.wsgi.application'
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "toolbox.context_processors.site",
)

from django.core.exceptions import SuspiciousOperation

def skip_suspicious_operations(record):
  if record.exc_info:
    exc_value = record.exc_info[1]
    if isinstance(exc_value, SuspiciousOperation):
      return False
  return True

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
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
         },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
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
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}

# Cache
CACHE_MIDDLEWARE_SECONDS = 60 * 5
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_KEY_PREFIX  = ''
DJANGO_MEMCACHED_REQUIRE_STAFF = True

try:
    from settings_dev import *
except ImportError:
    from settings_prod import *
TEMPLATE_DEBUG = DEBUG

# if DEBUG_TOOLBAR:
#     # Debugging toolbar middleware
#     MIDDLEWARE_CLASSES += (
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     )
#     # JavaScript panels for the deveopment debugging toolbar
#     DEBUG_TOOLBAR_PANELS = (
#         'debug_toolbar.panels.versions.VersionsPanel',
#         'debug_toolbar.panels.timer.TimerPanel',
#         'debug_toolbar.panels.settings.SettingsPanel',
#         'debug_toolbar.panels.headers.HeadersPanel',
#         'debug_toolbar.panels.request.RequestPanel',
#         'debug_toolbar.panels.profiling.ProfilingPanel',
#         'debug_toolbar.panels.sql.SQLPanel',
#         'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#         'debug_toolbar.panels.templates.TemplatesPanel',
#         'debug_toolbar.panels.cache.CachePanel',
#         'debug_toolbar.panels.signals.SignalsPanel',
#         'debug_toolbar.panels.logging.LoggingPanel',
#         'debug_toolbar.panels.redirects.RedirectsPanel',
#     )
#     # Debug toolbar app
#     INSTALLED_APPS += ('debug_toolbar',)
#     CONFIG_DEFAULTS = {
#         'INTERCEPT_REDIRECTS': False,
#     }
