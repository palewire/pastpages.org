from django.contrib.sitemaps import Sitemap
from models import Site


class SiteSitemap(Sitemap):
    changefreq = "hourly"
    
    def items(self):
        return Site.objects.filter(status='active')
    
    def lastmod(self, obj):
        try:
            s = obj.screenshot_set.all().order_by("-timestamp")[0]
            return s.timestamp
        except IndexError:
            return None


SITEMAPS = {
    'sites': SiteSitemap,
}
