"""
Memento timemap syndication
"""
from archive.models import Site
from django.shortcuts import get_object_or_404
from toolbox.timemap import TimemapLinkList, TimemapLinkIndex


class SiteTimemapLinkIndex(TimemapLinkIndex):
    """
    Returns a memento timemap index linking to other timemaps of screenshots
    archived for a site in our database.
    """
    pass


class SiteTimemapLinkList(TimemapLinkList):
    """
    Returns a memento timemap of screenshots archived for a site in our
    database.
    """
    limit = 10

    def get_object(self, request, url):
        return get_object_or_404(Site, url__startswith=url)

    def get_original_url(self, obj):
        return obj.url

    def items(self, obj):
        return obj.screenshot_set.all()

    def item_datetime(self, item):
        return item.timestamp
