import os, sys
import newrelic.agent

sys.path.append('/apps/pastpages.org/')
sys.path.append('/apps/pastpages.org/repo/')
sys.path.append('/apps/pastpages.org/lib/python2.7/site-packages/')
sys.path.append('/apps/pastpages.org/bin/')
sys.path.append('/apps/pastpages.org/src/')

newrelic.agent.initialize('/apps/pastpages.org/repo/project/newrelic.ini')

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ["CELERY_LOADER"] = "django"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
application = newrelic.agent.wsgi_application()(application)
