"""
Memento timemap syndication
"""
from archive.models import Site
from memento.timemap import TimemapLinkList
from django.shortcuts import get_object_or_404


class SiteTimemapLinkList(TimemapLinkList):
    """
    Returns a memento timemap of screenshots archived for a site in our
    database.
    """
    paginate_by = 1000

    def get_object(self, request, url):
        return get_object_or_404(Site, url__startswith=url)

    def get_original_url(self, obj):
        return obj.url

    def memento_list(self, obj):
        return obj.screenshot_set.all()

    def memento_datetime(self, item):
        return item.timestamp
