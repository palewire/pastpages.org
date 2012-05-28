from django.db.models import Count
from archive.models import Update, Site
from django.contrib.syndication.views import Feed


class RecentUpdates(Feed):
    title = "Latest updates from PastPages"
    link = "http://www.pastpages.org/"

    def items(self):
        qs = Update.objects.all()
        qs = qs.annotate(count=Count("screenshot"))
        sites = Site.objects.active().count()
        cutoff = int(sites * 0.7)
        return qs.filter(count__gte=cutoff)[:10]
    
    def item_pubdate(self, item):
        return item.start
