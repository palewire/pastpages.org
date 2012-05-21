from django.contrib.sites.models import Site
from django.http import HttpResponsePermanentRedirect
from django.core.urlresolvers import resolve
from django.core import urlresolvers
from django.utils.http import urlquote


class DomainRedirectMiddleware(object):
    """
    Redirect traffic to all sibling domains to http://palewi.re
    """
    host = 'pastpages.org'
    
    def update_uri(self, request):
        return '%s://%s%s%s' % (
            request.is_secure() and 'https' or 'http',
            self.host,
            urlquote(request.path),
            (request.method == 'GET' and len(request.GET) > 0) and '?%s' % request.GET.urlencode() or ''
        )
    
    def process_request(self, request):
        host = request.get_host()
        if host == 'www.pastpages.org':
            new_uri = self.update_uri(request)
            return HttpResponsePermanentRedirect(new_uri)
