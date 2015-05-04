from django.utils import six
from django.templatetags.tz import utc
from django.utils.timezone import is_naive
from django.http import Http404, HttpResponse
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
        self.request = request
        self.current_site = get_current_site(request)
        self.queryset = self.__get_dynamic_attr('memento_list', obj)
        feedgen = self.get_feed(obj)
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

    def get_page_number(self):
        page = self.request.GET.get(self.page_kwarg) or None
        if not page:
            return None
        try:
            return int(page)
        except ValueError:
            raise Http404("Page can't be converted to an int.")

    def get_paginator(self, queryset):
        return self.paginator_class(queryset, self.paginate_by)

    def get_page(self, page_number):
        paginator = self.get_paginator(self.queryset)
        try:
            return paginator.page(page_number)
        except InvalidPage as e:
            raise Http404('Invalid page (%(page_number)s): %(message)s' % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_list_feed(self, obj, page_number=None):
        feed_type = TimemapLinkListGenerator
        feed = feed_type(
            original_url=self.get_original_url(obj),
            timemap_url=add_domain(
                self.current_site.domain,
                self.request.path,
                self.request.is_secure(),
            ),
        )
        if page_number:
            self.queryset = self.get_page(page_number).object_list
        for item in self.queryset:
            link = add_domain(
                self.current_site.domain,
                self.__get_dynamic_attr('memento_link', item),
                self.request.is_secure(),
            )
            item_datetime = self.__get_dynamic_attr('memento_datetime', item)
            if item_datetime and is_naive(item_datetime):
                item_datetime = utc(item_datetime)
            feed.add_item(
                link=link,
                datetime=item_datetime,
            )
        return feed

    def get_index_feed(self, obj):
        feed_type = TimemapLinkIndexGenerator
        timemap_url = add_domain(
            self.current_site.domain,
            self.request.path,
            self.request.is_secure(),
        )
        feed = feed_type(
            original_url=self.get_original_url(obj),
            timemap_url=timemap_url,
        )
        paginator = self.get_paginator(self.queryset)
        for page in paginator.page_range:
            link = add_domain(
                self.current_site.domain,
                "%s?%s=%s" % (timemap_url, self.page_kwarg, page),
                self.request.is_secure(),
            )
            feed.add_item(link=link)
        return feed

    def get_feed(self, obj):
        """
        Returns a feedgenerator.DefaultFeed object, fully populated, for
        this feed. Raises FeedDoesNotExist for invalid parameters.
        """
        if self.paginate_by:
            page_number = self.get_page_number()
            if page_number:
                return self.get_list_feed(obj, page_number)
            else:
                return self.get_index_feed(obj)
        else:
            return self.get_list_feed(obj)
