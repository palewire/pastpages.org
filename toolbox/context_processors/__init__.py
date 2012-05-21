from django.conf import settings
from django.contrib.sites.models import Site


def site(request):
    """
    A context processor to add the site to the current Context
    """
    try:
        current_site = Site.objects.get_current()
        return {
            'site': current_site,
        }
    except Site.DoesNotExist:
        # always return a dict, no matter what!
        return {'site':''} # an empty string
