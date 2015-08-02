"""
Memento timemap syndication
"""
import logging
from archive.models import Site, Screenshot
from memento.timemap import TimemapLinkList
from django.shortcuts import get_object_or_404
logger = logging.getLogger(__name__)


class SiteTimemapLinkList(TimemapLinkList):
    """
    Returns a TimeMap of screenshots archived
    for a site in our database
    """
    paginate_by = 1000

    def get_object(self, request, url):
        return get_object_or_404(Site, url__startswith=url)

    def get_original_url(self, obj):
        return obj.url

    def memento_list(self, obj):
        return Screenshot.objects.filter(
            site=obj
        ).only("id", "timestamp")

    def memento_datetime(self, item):
        return item.timestamp
