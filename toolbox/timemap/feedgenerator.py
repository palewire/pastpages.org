from django.utils import six
from django.utils.six import StringIO
from django.utils import tzinfo
from django.template.loader import get_template, render_to_string
from django.utils.timezone import is_naive
from django.utils.feedgenerator import rfc3339_date
from django.contrib.syndication.views import Feed, add_domain
from django.contrib.sites.models import get_current_site
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import iri_to_uri
from django.core.exceptions import ImproperlyConfigured


class TimemapLinkFeedGenerator(object):
    "Base class for all syndication feeds. Subclasses should provide write()"
    mime_type = 'application/rss+xml; charset=utf-8'

    def __init__(self, original_url, timemap_url, **kwargs):
        self.feed = {
            'original_url': iri_to_uri(original_url),
            'timemap_url': iri_to_uri(timemap_url),
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

    def minimum_datetime(self):
        """
        Returns the earliest datetime in the item list.
        """
        return min([i['datetime'] for i in self.items])

    def maximum_datetime(self):
        """
        Returns the latest datetime in the item list.
        """
        return max([i['datetime'] for i in self.items])

    def write(self, outfile, encoding):
        context = {
            'original_url': self.feed['original_url'],
            'timemap_url': self.feed['timemap_url'],
            'minimum_datetime': self.minimum_datetime(),
            'maximum_datetime': self.maximum_datetime(),
            'items': sorted(self.items, key=lambda x:x['datetime']),
        }
        s = render_to_string("timemap/link_list.txt", context)
        outfile.write(s)

    def writeString(self, encoding):
        """
        Returns the feed in the given encoding as a string.
        """
        s = StringIO()
        self.write(s, encoding)
        return s.getvalue()