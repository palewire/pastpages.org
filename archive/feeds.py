from django.db.models import Count
from archive.models import Update, Site
from django.utils import timezone
from django.shortcuts import get_object_or_404
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
    def get_object(self, request, pk):
        """
        Fetch the Site object.
        """
        return get_object_or_404(Site, pk=pk)
        
    def title(self, obj):
        """
        Set the feed title.
        """
        return "%s screenshots by PastPages" % obj.name.lower()
    
    def link(self, obj):
        """
        Set the feed link.
        """
        return obj.get_absolute_url()
        
    def items(self, obj):
        """
        Fetch the latest 10 screenshots
        """
        return obj.screenshot_set.all()[:10]
