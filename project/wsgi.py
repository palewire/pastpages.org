import os, sys
sys.path.append('/apps/pastpages.org/')
sys.path.append('/apps/pastpages.org/repo/')
sys.path.append('/apps/pastpages.org/lib/python2.7/site-packages/')
sys.path.append('/apps/pastpages.org/bin/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ["CELERY_LOADER"] = "django"
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
