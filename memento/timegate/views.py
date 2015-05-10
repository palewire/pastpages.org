from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.views.generic import RedirectView
from dateutil.parser import parse as dateparser
from django.utils.cache import patch_vary_headers
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from django.contrib.syndication.views import add_domain
from django.contrib.sites.models import get_current_site


class TimeGateView(RedirectView):
    """
    A Memento TimeGate that parses a request from the headers
    and redirects to the corresponding screenshot detail page.
    """
    model = None
    queryset = None
    timemap_pattern_name = None
    url_kwarg = 'url'
    url_field = 'url'
    datetime_field = 'datetime'

    def parse_datetime(self, request):
        # Verify that the Accept-Datetime header is provided
        if not request.META.get("HTTP_ACCEPT_DATETIME"):
            return None

        # Verify that the Accept-Datetime header is valid
        dt = dateparser(request.META.get("HTTP_ACCEPT_DATETIME"))
        if not dt:
            return HttpResponse(
                _("Bad request (400): Accept-Datetime header is malformed"),
                status=400
            )
        return dt

    def get_object(self, url, dt):
        queryset = self.get_queryset()
        queryset = queryset.filter(**{self.url_field: url})

        try:
            prev_obj = queryset.filter(
                **{"%s__lte" % self.datetime_field: dt}
            ).order_by("-%s" % self.datetime_field)[0]
        except IndexError:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        try:
            next_obj = queryset.filter(
                **{"%s__gte" % self.datetime_field: dt}
            ).order_by("%s" % self.datetime_field)[0]
        except IndexError:
            next_obj = None

        if not next_obj:
            return prev_obj
        else:
            prev_delta = abs(dt - getattr(prev_obj, self.datetime_field))
            next_delta = abs(dt - getattr(next_obj, self.datetime_field))
            if prev_delta <= next_delta:
                return prev_obj
            else:
                return next_obj

    def get_most_recent_object(self, url):
        queryset = self.get_queryset()
        try:
            return queryset.filter(**{
                self.url_field: url,
            }).order_by("-%s" % self.datetime_field)[0]
        except IndexError:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

    def get_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the object.
        Note that this method is called by the default implementation of
        `get_object` and may not be called if `get_object` is overridden.
        """
        if self.queryset is None:
            if self.model:
                return self.model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.queryset.all()

    def get_redirect_url(self, request, obj):
        current_site = get_current_site(request)
        return add_domain(
            current_site.domain,
            obj.get_absolute_url(),
            request.is_secure(),
        )

    def get_timemap_url(self, request, url):
        path = reverse(self.timemap_pattern_name, kwargs={'url': url})
        current_site = get_current_site(request)
        return add_domain(
            current_site.domain,
            path,
            request.is_secure(),
        )

    def get(self, request, *args, **kwargs):
        url = self.kwargs.get(self.url_kwarg)
        if not url:
            return HttpResponse(
                _("Bad request (400): URL not provided"),
                status=400
            )
        url = url.replace("http:/", "http://")
        url = url.replace("http:///", "http://")
        dt = self.parse_datetime(request)
        if dt:
            obj = self.get_object(url, dt)
        else:
            obj = self.get_most_recent_object(url)
        redirect_url = self.get_redirect_url(request, obj)
        response = HttpResponse(status=302)
        patch_vary_headers(response, ["accept-datetime"])
        if self.timemap_pattern_name:
            response['Link'] = """<%(url)s>; rel="original", \
<%(timemap_url)s>; rel="timemap"; type="application/link-format\"""" % dict(
                url=url,
                timemap_url=self.get_timemap_url(request, url)
            )
        response['Location'] = redirect_url
        return response
