from tastypie import fields
from archive.models import Site
from django.conf import settings
from tastypie.serializers import Serializer
from django.core.urlresolvers import reverse
from tastypie.resources import ModelResource
from django.conf.urls.defaults import url
# Diff throttle depending on env
if settings.PRODUCTION:
    from tastypie.throttle import CacheThrottle as Throttle
else:
    from tastypie.throttle import BaseThrottle as Throttle


class SiteResource(ModelResource):
    
    class Meta:
        resource_name = 'sites'
        queryset = Site.objects.active()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = Serializer(formats=['json', 'jsonp'],
            content_types = {
                'json': 'text/javascript',
                'jsonp': 'text/javascript'
        })
        include_absolute_url = True
        filtering = {
            "slug": ('exact',),
        }
