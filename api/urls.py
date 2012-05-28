import resources
from tastypie.api import Api
from django.conf.urls.defaults import *

api = Api(api_name='beta')
api.register(resources.ScreenshotResource(), canonical=True)
api.register(resources.SiteResource(), canonical=True)
api.register(resources.TagResource(), canonical=True)
api.register(resources.UpdateResource(), canonical=True)

urlpatterns = api.urls
