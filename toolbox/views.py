from django import http
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.cache import cache
from django.template import RequestContext

import datetime, re

def cache_status(request):
    try:
        import memcache
    except ImportError:
        raise http.Http404

    if not (request.user.is_authenticated() and request.user.is_staff):
        raise http.Http404
    
    stats = cache._cache.get_stats()   #Beware, using _cache, may change
    
    per_server_stats = []
    for server, server_stats in stats:
        server_stats['server_name'] = server
        try:
            server_stats['hit_rate'] = 100 * float(server_stats['get_hits']) / float(server_stats['cmd_get'])
        except Exception, e:
            server_stats['hit_rate'] = str(e)
        per_server_stats.append(server_stats)
    
    context = dict(per_server_stats=per_server_stats, time=datetime.datetime.now())
    return render_to_response('memcachestatus/index.html', context, context_instance=RequestContext(request))
