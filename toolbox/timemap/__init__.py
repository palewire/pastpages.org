from django.utils import six
from django.core import paginator
from django.templatetags.tz import utc
from django.utils.http import http_date
from django.utils.timezone import is_naive
from django.http import Http404, HttpResponse
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import get_current_site
from django.core.paginator import InvalidPage, Paginator
from django.contrib.syndication.views import add_domain
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from .feedgenerator import TimemapLinkListGenerator, TimemapLinkIndexGenerator


class TimemapLinkList(object):
    """
    An feed class that returns a list in Memento's Timemap format.
    """
    paginator_class = Paginator
    paginate_by = None
    page_kwarg = 'page'

    def __call__(self, request, *args, **kwargs):
        try:
            obj = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404('Feed object does not exist.')
        feedgen = self.get_feed(obj, request)
        response = HttpResponse(content_type=feedgen.mime_type)
        feedgen.write(response, 'utf-8')
        return response

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

    def memento_datetime(self, item):
        raise ImproperlyConfigured('Define an item_datetime() method in \
your %s class.' % self.__class__.__name__)

    def memento_link(self, memento):
        try:
            return memento.get_absolute_url()
        except AttributeError:
            raise ImproperlyConfigured(
                'Give your %s class a get_absolute_url() method, or define a '
                'memento() method in your TimemapLinkList class.' % (
                    memento.__class__.__name__
                )
            )

    def get_page(self, queryset, request):
        paginator = self.paginate_queryset(queryset)
        page = request.GET.get(self.page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            raise Http404("Page can't be converted to an int.")
        try:
            print queryset, page_number
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404('Invalid page (%(page_number)s): %(message)s' % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_queryset(self, obj):
        return self.__get_dynamic_attr('memento_list', obj)

    def paginate_queryset(self, queryset):
        return self.paginator_class(queryset, self.paginate_by)

    def get_feed_type(self):
        return TimemapLinkListGenerator

    def get_feed(self, obj, request):
        """
        Returns a feedgenerator.DefaultFeed object, fully populated, for
        this feed. Raises FeedDoesNotExist for invalid parameters.
        """
        feed_type = self.get_feed_type()
        current_site = get_current_site(request)
        feed = feed_type(
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
                self.__get_dynamic_attr('memento_link', item),
                request.is_secure(),
            )
            item_datetime = self.__get_dynamic_attr('memento_datetime', item)
            if item_datetime and is_naive(item_datetime):
                item_datetime = utc(item_datetime)
            feed.add_item(
                link = link,
                datetime = item_datetime,
            )
        return feed
