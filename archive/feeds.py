"""
RSS feed syndication
"""
# Models
from django.db.models import Count
from taggit.models import Tag, TaggedItem
from archive.models import Update, Site, Screenshot

# Feeds
from toolbox.mrss import MediaRSSFeed
from django.contrib.syndication.views import Feed

# Misc
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import date as dateformat


class RecentUpdates(Feed):
    """
    The latest updates published by PastPages.
    """
    title = "Latest updates from PastPages"
    link = "http://www.pastpages.org/"

    def items(self):
        return Update.objects.all().order_by('-start')[:20]

    def item_pubdate(self, item):
        return item.start

    def item_title(self, item):
        return u'Screenshots taken at %s' % dateformat(
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

    def get_object(self, request, slug):
        return get_object_or_404(Site, slug=slug)

    def title(self, obj):
        return u'%s screenshots by PastPages' % obj.name

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        return obj.screenshot_set.all()[:10]

    def item_title(self, item):
        return u'Screenshots of %s taken at %s' % (
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


class TagFeed(Feed):
    """
    The most recent pages from a tag.
    """
    feed_type = MediaRSSFeed

    def get_object(self, request, slug):
        return get_object_or_404(Tag, slug=slug)

    def title(self, obj):
        return u"Screenshots of sites tagged as %s by PastPages" % obj.name

    def link(self, obj):
        return reverse('archive-tag-detail', args=[obj.slug])

    def items(self, obj):
        site_list = [i.content_object for i in
            TaggedItem.objects.filter(tag=obj)
        ]
        update = Update.objects.live()
        return Screenshot.objects.filter(
            update=update,
            site__in=site_list,
            has_crop=True,
            has_image=True,
        )

    def item_title(self, item):
        return u'Screenshots of %s taken at %s' % (
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
