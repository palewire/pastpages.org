import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ["CELERY_LOADER"] = "django"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
