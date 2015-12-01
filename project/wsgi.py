import os, sys

sys.path.append('/apps/pastpages.org/')
sys.path.append('/apps/pastpages.org/repo/')
sys.path.append('/apps/pastpages.org/lib/python2.7/site-packages/')
sys.path.append('/apps/pastpages.org/bin/')
sys.path.append('/apps/pastpages.org/src/')
sys.path.append('/apps/pastpages.org/src/django_memento_framework-master/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ["CELERY_LOADER"] = "django"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
try:
    import newrelic.agent
    application = newrelic.agent.wsgi_application()(application)
    newrelic.agent.initialize('/apps/pastpages.org/repo/project/newrelic.ini')
except:
    pass
