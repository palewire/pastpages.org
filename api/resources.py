"""
Configuration of a public API that user django-tastypie
"""
# Misc.
from django.conf import settings
from django.utils.timezone import is_naive

# Models
from taggit.models import Tag, TaggedItem
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


class MyDateSerializer(Serializer):
    """
    Our own serializer to format datetimes in ISO 8601 but with timezone
    offset.
    """
    def format_datetime(self, data):
        # If naive or rfc-2822, default behavior...
        if is_naive(data) or self.datetime_formatting == 'rfc-2822':
            return super(MyDateSerializer, self).format_datetime(data) 
        return data.isoformat()

# Configure out serializer for the site
PastPagesSerializer = MyDateSerializer(
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
        max_limit = 100
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
    
    def build_filters(self, filters=None):
        """
        Override build_filters to support geoqueries.
        """
        if filters is None:
            filters = {}
        orm_filters = super(ScreenshotResource, self).build_filters(filters)
        # Check if there are any tag filters
        tag_filters = [d for d in orm_filters.keys() if d.startswith("site__tags__")]
        if tag_filters:
            # If so grab the filter and value
            k = tag_filters[0]
            v = orm_filters[k]
            # Split off the stuff we don't need
            # on the front of the filter
            f = k.split("site__tags__")[1]
            # Pull the tag
            tag = Tag.objects.filter(**{f:v})
            # Pull the related sites
            site_list = [i.content_object for i in
                TaggedItem.objects.filter(tag=tag)
            ]
            # Clear out the filter we started with
            del orm_filters[k]
            # Add the new one we've created
            orm_filters.update({'site__in': site_list})
        return orm_filters


class SiteResource(ModelResource):
    """
    Instructions for how to serialize the Site model.
    """
    tags = fields.ToManyField('api.resources.TagResource', 'tags')
    
    class Meta:
        resource_name = 'sites'
        max_limit = 100
        queryset = Site.objects.active()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer
        include_absolute_url = True
        filtering = {
            "name": ALL,
            "slug": ALL,
            "tags": ALL_WITH_RELATIONS,
        }


class TagResource(ModelResource):
    """
    Instructions for how to serialize the Tag model.
    """
    class Meta:
        resource_name = 'tags'
        max_limit = 100
        queryset = Tag.objects.all()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer
        filtering = {
            "name": ALL,
            "slug": ALL,
        }


class UpdateResource(ModelResource):
    """
    Instructions for how to serialize the Update model.
    """
    screenshots = fields.ToManyField('api.resources.ScreenshotResource', 'screenshot_set')
    
    class Meta:
        resource_name = 'updates'
        max_limit = 100
        queryset = Update.objects.all()
        allowed_methods = ['get',]
        throttle = Throttle(throttle_at=50)
        serializer = PastPagesSerializer
        include_absolute_url = True
