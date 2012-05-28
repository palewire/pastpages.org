from tastypie import fields
from django.conf import settings
from taggit.models import Tag
from tastypie.serializers import Serializer
from django.core.urlresolvers import reverse
from tastypie.resources import ModelResource
from django.conf.urls.defaults import url
from archive.models import Site, Update, Screenshot
# Diff throttle depending on env
if settings.PRODUCTION:
    from tastypie.throttle import CacheThrottle as Throttle
else:
    from tastypie.throttle import BaseThrottle as Throttle


# Configure out serializer for the site
PastPagesSerializer = Serializer(
    formats=['json', 'jsonp' , 'plist', 'xml', 'yaml'],
    content_types = {
        'json': 'text/javascript',
        'jsonp': 'text/javascript',
        'plist': 'application/x-plist',
        'xml': "text/xml",
        'yaml': 'text/yaml',
})

class ScreenshotResource(ModelResource):
    update = fields.ToOneField('api.resources.UpdateResource', 'update')
    site = fields.ToOneField('api.resources.SiteResource', 'site')
    
    class Meta:
        resource_name = 'screenshots'
        queryset = Screenshot.objects.filter(site__status='active').select_related("update")
        excludes = ['has_html', 'html_archived', 'html_raw']
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer
        include_absolute_url = True


class SiteResource(ModelResource):
    tags = fields.ToManyField('api.resources.TagResource', 'tags')
    
    class Meta:
        resource_name = 'sites'
        queryset = Site.objects.active()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer
        include_absolute_url = True
        filtering = {
            "slug": ('exact',),
        }


class TagResource(ModelResource):
    
    class Meta:
        resource_name = 'tags'
        queryset = Tag.objects.all()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer


class UpdateResource(ModelResource):
    screenshots = fields.ToManyField('api.resources.ScreenshotResource', 'screenshot_set')
    
    class Meta:
        resource_name = 'updates'
        queryset = Update.objects.all()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer
        include_absolute_url = True
