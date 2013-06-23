"""
Configuration of a public API that user django-tastypie
"""
# Misc.
from django.conf import settings
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import url

# Models
from taggit.models import Tag
from archive.models import Site, Update, Screenshot

# Tastypie
from tastypie import fields
from tastypie.serializers import Serializer
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS

# Diff throttle depending on env
if settings.PRODUCTION:
    from tastypie.throttle import CacheThrottle as Throttle
else:
    from tastypie.throttle import BaseThrottle as Throttle

# Configure out serializer for the site
PastPagesSerializer = Serializer(
    formats=['json', 'jsonp' , 'plist', 'xml', 'yaml'],
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'plist': 'application/x-plist',
        'xml': "text/xml",
        'yaml': 'text/yaml',
})

#
# API resources
#


class ScreenshotResource(ModelResource):
    """
    Instructions for how to serialize the Screenshot model.
    """
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
        filtering = {
            "site": ALL_WITH_RELATIONS,
            "timestamp": ALL,
        }


class SiteResource(ModelResource):
    """
    Instructions for how to serialize the Site model.
    """
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
    """
    Instructions for how to serialize the Tag model.
    """
    class Meta:
        resource_name = 'tags'
        queryset = Tag.objects.all()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer


class UpdateResource(ModelResource):
    """
    Instructions for how to serialize the Update model.
    """
    screenshots = fields.ToManyField('api.resources.ScreenshotResource', 'screenshot_set')
    
    class Meta:
        resource_name = 'updates'
        queryset = Update.objects.all()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer
        include_absolute_url = True
