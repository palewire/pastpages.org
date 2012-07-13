from taggit.models import Tag
from django.contrib.sitemaps import Sitemap
from models import Site, Update, Screenshot
from django.core.urlresolvers import reverse


class AbstractSitemapClass():
    url = None
    
    def get_absolute_url(self):
        return self.url


class ScreenshotSitemap(Sitemap):
    changefreq = "never"
    limit = 1000
    
    def items(self):
        return Screenshot.objects.filter(has_image=True)
    
    def lastmod(self, obj):
        return obj.timestamp


class SiteSitemap(Sitemap):
    changefreq = "hourly"
    
    def items(self):
        return Site.objects.active()
    
    def lastmod(self, obj):
        try:
            s = obj.screenshot_set.all().order_by("-timestamp")[0]
            return s.timestamp
        except IndexError:
            return None


class StaticSitemap(Sitemap):
    pages = {
        'index':'/',
        'about':'/about/',
        'champions': '/champions/',
        'contact': '/contact/',
        'feeds': '/feeds/',
    }
    main_sitemaps = []
    for page in pages.keys():
        sitemap_class = AbstractSitemapClass()
        sitemap_class.url = pages[page]
        main_sitemaps.append(sitemap_class)
    
    def items(self):
        return self.main_sitemaps


class UpdateSitemap(Sitemap):
    changefreq = "never"
    limit = 1000
    
    def items(self):
        return Update.objects.all()
    
    def lastmod(self, obj):
        return obj.start


class TagSitemap(Sitemap):
    changefreq = "hourly"
    
    def items(self):
        return Tag.objects.all()
    
    def location(self, obj):
        return reverse('archive-tag-detail', args=[obj.name])


SITEMAPS = {
    'screenshots': ScreenshotSitemap,
    'sites': SiteSitemap,
    'static': StaticSitemap,
    'tags': TagSitemap,
    'updates': UpdateSitemap,
}
