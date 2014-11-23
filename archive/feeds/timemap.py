"""
Memento timemap syndication
"""
from archive.models import Site
from django.utils import six
from django.utils.six import StringIO
from django.shortcuts import get_object_or_404
from django.utils.timezone import is_naive
from django.utils import tzinfo
from django.utils.feedgenerator import rfc3339_date
from django.contrib.syndication.views import Feed, add_domain
from django.contrib.sites.models import get_current_site
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import iri_to_uri
from django.core.exceptions import ImproperlyConfigured


class TimemapLinkFeedGenerator(object):
    "Base class for all syndication feeds. Subclasses should provide write()"
    mime_type = 'application/rss+xml; charset=utf-8'

    def __init__(self, link, **kwargs):
        self.feed = {
            'link': iri_to_uri(link),
        }
        self.feed.update(kwargs)
        self.items = []

    def add_item(self, link, datetime, **kwargs):
        """
        Adds an item to the feed.
        """
        item = {
            'link': iri_to_uri(link),
            'datetime': datetime,
        }
        item.update(kwargs)
        self.items.append(item)

    def num_items(self):
        return len(self.items)

    def root_attributes(self):
        return

    def add_root_elements(self, handler):
        handler.addQuickElement("link", self.feed['link'])

    def write_items(self, handler):
        for item in self.items:
            handler.startElement("entry", {})
            self.add_item_elements(handler, item)
            handler.endElement("entry")

    def add_item_elements(self, handler, item):
        handler.addQuickElement("link", "", {
            "href": item['link'],
            "rel": "memento"
        })
        handler.addQuickElement("datetime", rfc3339_date(item['datetime']))

    def write(self, outfile, encoding):
        handler = SimplerXMLGenerator(outfile, encoding)
        handler.startDocument()
        self.add_root_elements(handler)
        self.write_items(handler)
        handler.endElement("rss")

    def writeString(self, encoding):
        """
        Returns the feed in the given encoding as a string.
        """
        s = StringIO()
        self.write(s, encoding)
        return s.getvalue()


class TimemapLinkFeed(Feed):
    """
    An feed class that returns a list in Memento's Timemap format.
    """
    feed_type = TimemapLinkFeedGenerator

    def item_datetime(self, item):
        raise ImproperlyConfigured('Define an item_datetime() method in \
your %s class.' % self.__class__.__name__)

    def __get_dynamic_attr(self, attname, obj, default=None):
        try:
            attr = getattr(self, attname)
        except AttributeError:
            return default
        if callable(attr):
            # Check co_argcount rather than try/excepting the function and
            # catching the TypeError, because something inside the function
            # may raise the TypeError. This technique is more accurate.
            try:
                code = six.get_function_code(attr)
            except AttributeError:
                code = six.get_function_code(attr.__call__)
            if code.co_argcount == 2:       # one argument is 'self'
                return attr(obj)
            else:
                return attr()
        return attr

    def get_feed(self, obj, request):
        """
        Returns a feedgenerator.DefaultFeed object, fully populated, for
        this feed. Raises FeedDoesNotExist for invalid parameters.
        """
        current_site = get_current_site(request)
        link = self.get_object_link(obj)
        feed = self.feed_type(
            link = obj.url,
        )

        for item in self.__get_dynamic_attr('items', obj):
            link = add_domain(
                current_site.domain,
                self.__get_dynamic_attr('item_link', item),
                request.is_secure(),
            )

            datetime = self.__get_dynamic_attr('item_datetime', item)
            if datetime and is_naive(datetime):
                utc = tzinfo.LocalTimezone(datetime)
                datetime = datetime.replace(tzinfo=utc)

            feed.add_item(
                link = link,
                datetime = datetime,
            )
        return feed


class SiteTimemapLinkFeed(TimemapLinkFeed):
    """
    Returns a memento timemap of screenshots archived for a site in our
    database.
    """
    def get_object(self, request, url):
        return get_object_or_404(Site, url="http://www.bbc.co.uk/news/")

    def get_object_link(self, obj):
        return obj.url

    def items(self, obj):
        return obj.screenshot_set.all()[:10]

    def item_datetime(self, item):
        return item.timestamp


"""
<http://www.cs.odu.edu/~mln/>; rel="original",
<http://archive.today/timegate/http://www.cs.odu.edu/~mln/>; rel="timegate",
<http://archive.today/20130618185742/http://www.cs.odu.edu/~mln/>; rel="first memento"; datetime="Tue, 18 Jun 2013 18:57:42 GMT",
<http://archive.today/20130621194047/http://www.cs.odu.edu/~mln/>; rel="memento"; datetime="Fri, 21 Jun 2013 19:40:47 GMT",
<http://archive.today/20130723172543/http://www.cs.odu.edu/~mln/>; rel="memento"; datetime="Tue, 23 Jul 2013 17:25:43 GMT",
<http://archive.today/20130723173951/http://www.cs.odu.edu/~mln/>; rel="memento"; datetime="Tue, 23 Jul 2013 17:39:51 GMT",
<http://archive.today/20130728010336/http://www.cs.odu.edu/~mln/>; rel="memento"; datetime="Sun, 28 Jul 2013 01:03:36 GMT",
<http://archive.today/20131217200455/http://www.cs.odu.edu/~mln/>; rel="memento"; datetime="Tue, 17 Dec 2013 20:04:55 GMT",
<http://archive.today/20141015185128/http://www.cs.odu.edu/~mln/>; rel="memento"; datetime="Wed, 15 Oct 2014 18:51:28 GMT",
<http://archive.today/20141020194524/http://www.cs.odu.edu/~mln/>; rel="memento"; datetime="Mon, 20 Oct 2014 19:45:24 GMT",
<http://archive.today/20141112185338/http://www.cs.odu.edu/~mln/>; rel="memento"; datetime="Wed, 12 Nov 2014 18:53:38 GMT",
<http://archive.today/20141120172147/http://www.cs.odu.edu/~mln/>; rel="last memento"; datetime="Thu, 20 Nov 2014 17:21:47 GMT",
<http://archive.today/timemap/http://www.cs.odu.edu/~mln/>; rel="self"; type="application/link-format"; from="Tue, 18 Jun 2013 18:57:42 GMT"; until="Thu, 20 Nov 2014 17:21:47 GMT"
"""