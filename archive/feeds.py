from taggit.models import Tag
from django.db.models import Count
from archive.models import Update, Site
from django.utils import timezone
from django.shortcuts import get_object_or_404
from toolbox.mrss import MediaRSSFeed
from django.template.defaultfilters import date as dateformat
from django.contrib.syndication.views import Feed, FeedDoesNotExist


class RecentUpdates(Feed):
    title = "Latest updates from PastPages"
    link = "http://www.pastpages.org/"
    
    def items(self):
        qs = Update.objects.all()
        # Count how many screenshots they have
        qs = qs.annotate(count=Count("screenshot"))
        # And limit it to those that are at least near completion.
        sites = Site.objects.active().count()
        cutoff = int(sites * 0.7)
        return qs.filter(count__gte=cutoff)[:10]
    
    def item_pubdate(self, item):
        return item.start
    
    def item_title(self, item):
        return 'Screenshots taken at %s' % dateformat(
            timezone.localtime(item.start),
            'l N j, Y, P e',
        )
    
    def item_description(self, item):
        return None


class SiteFeed(Feed):
    """
    The most recent pages from a site.
    """
    feed_type = MediaRSSFeed
    
    def get_object(self, request, pk):
        return get_object_or_404(Site, pk=pk)
        
    def title(self, obj):
        return "%s screenshots by PastPages" % obj.name
    
    def link(self, obj):
        return obj.get_absolute_url()
        
    def items(self, obj):
        return obj.screenshot_set.all()[:10]
    
    def item_title(self, item):
        return 'Screenshots of %s taken at %s' % (
            item.site,
            dateformat(
                timezone.localtime(item.timestamp),
                'l N j, Y, P e',
            )
        )
    
    def item_description(self, item):
        return None
    
    def item_extra_kwargs(self, item):
        d = {}
        if item.has_crop:
            d['thumbnail_url'] = item.crop.url_300x251
            d['content_url'] = item.crop.url
        return d

