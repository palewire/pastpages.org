import resources
from tastypie.api import Api
from django.conf.urls.defaults import *

api = Api(api_name='beta')
api.register(resources.SiteResource(), canonical=True)

urlpatterns = api.urls
