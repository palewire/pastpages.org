"""
Memento timemap syndication
"""
from archive.models import Site
from toolbox.timemap import TimemapLinkList
from django.shortcuts import get_object_or_404



class SiteTimemapLinkFeed(TimemapLinkList):
    """
    Returns a memento timemap of screenshots archived for a site in our
    database.
    """
    def get_object(self, request, url):
        return get_object_or_404(Site, url__startswith=url)

    def get_original_url(self, obj):
        return obj.url

    def items(self, obj):
        return obj.screenshot_set.all()[:10]

    def item_datetime(self, item):
        return item.timestamp
