from django.utils import six
from django.http import Http404
from django.core import paginator
from django.templatetags.tz import utc
from django.utils.timezone import is_naive
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import get_current_site
from django.core.paginator import InvalidPage, Paginator
from django.contrib.syndication.views import Feed, add_domain
from .feedgenerator import TimemapLinkListGenerator, TimemapLinkIndexGenerator


class TimemapLinkIndex(Feed):
    feed_type = TimemapLinkIndexGenerator


class TimemapLinkList(Feed):
    """
    An feed class that returns a list in Memento's Timemap format.
    """
    feed_type = TimemapLinkListGenerator
    paginator_class = Paginator
    paginate_by = None
    page_kwarg = 'page'

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

    def item_datetime(self, item):
        raise ImproperlyConfigured('Define an item_datetime() method in \
your %s class.' % self.__class__.__name__)

    def get_feed(self, obj, request):
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
        if self.paginate_by:
            paginator, page, queryset, is_paginated = self.get_page(
                self.get_queryset(obj),
                request
            )
        else:
            queryset = self.get_queryset(obj)
        for item in queryset:
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

    def get_page(self, queryset, request):
        paginator = self.paginate_queryset(queryset)
        page = request.GET.get(self.page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            raise Http404("Page can't be converted to an int.")
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404('Invalid page (%(page_number)s): %(message)s' % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_queryset(self, obj):
        return self.__get_dynamic_attr('items', obj)

    def paginate_queryset(self, queryset):
        return self.paginator_class(queryset, self.paginate_by)
