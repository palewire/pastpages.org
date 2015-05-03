from django.utils import six
from django.core import paginator
from django.templatetags.tz import utc
from django.utils.timezone import is_naive
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import get_current_site
from django.contrib.syndication.views import Feed, add_domain
from .feedgenerator import TimemapLinkListGenerator, TimemapLinkIndexGenerator


class TimemapLinkIndex(Feed):
    feed_type = TimemapLinkIndexGenerator


class TimemapLinkList(Feed):
    """
    An feed class that returns a list in Memento's Timemap format.
    """
    limit = 50000
    feed_type = TimemapLinkListGenerator

    def item_datetime(self, item):
        raise ImproperlyConfigured('Define an item_datetime() method in \
your %s class.' % self.__class__.__name__)

    def get_paginator(self, obj):
        items = self.__get_dynamic_attr('items', obj)
        return paginator.Paginator(items, self.limit)

    def __get_dynamic_attr(self, attname, obj, default=None):
        try:
            attr = getattr(self, attname)
        except AttributeError:
            return default
        if callable(attr):
            try:
                code = six.get_function_code(attr)
            except AttributeError:
                code = six.get_function_code(attr.__call__)
            if code.co_argcount == 2:
                return attr(obj)
            else:
                return attr()
        return attr

    def get_feed(self, obj, request, page=1):
        """
        Returns a feedgenerator.DefaultFeed object, fully populated, for
        this feed. Raises FeedDoesNotExist for invalid parameters.
        """
        current_site = get_current_site(request)
        feed = self.feed_type(
            original_url = self.get_original_url(obj),
            timemap_url = add_domain(
                current_site.domain,
                request.path,
                request.is_secure(),
            ),
        )
        for item in self.get_paginator(obj).page(page).object_list:
            link = add_domain(
                current_site.domain,
                self.__get_dynamic_attr('item_link', item),
                request.is_secure(),
            )
            item_datetime = self.__get_dynamic_attr('item_datetime', item)
            if item_datetime and is_naive(item_datetime):
                item_datetime = utc(item_datetime)
            feed.add_item(
                link = link,
                datetime = item_datetime,
            )
        return feed