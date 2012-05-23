from django.contrib.sitemaps import Sitemap
from models import Site, Update, Screenshot


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


class UpdateSitemap(Sitemap):
    changefreq = "never"
    limit = 1000
    
    def items(self):
        return Update.objects.all()
    
    def lastmod(self, obj):
        return obj.start


class ScreenshotSitemap(Sitemap):
    changefreq = "never"
    limit = 1000
    
    def items(self):
        return Screenshot.objects.filter(has_image=True)
    
    def lastmod(self, obj):
        return obj.timestamp


SITEMAPS = {
    'sites': SiteSitemap,
    'updates': UpdateSitemap,
    'screenshots': ScreenshotSitemap,
}
