from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from archive import views, sitemaps
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.Index.as_view(),
        name='archive-index'),
    url(r'^cry-for-help/$', views.CryForHelp.as_view(),
        name='cry-for-help'),
    url(r'^site/(?P<slug>[-\w]+)/$', views.SiteDetail.as_view(),
        name='archive-site-detail'),
    url(r'^tag/(?P<slug>[-\w]+)/$', views.TagDetail.as_view(),
        name='archive-tag-detail'),
    url(r'^update/(?P<pk>\d+)/$', views.UpdateDetail.as_view(),
        name='archive-update-detail'),
    url(r'^date/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        views.DateDetail.as_view(),
        name='archive-date-detail'),
    url(r'^screenshot/(?P<pk>\d+)/$', views.ScreenshotDetail.as_view(),
        name='archive-screenshot-detail'),
    url(r'^cache/$', 'toolbox.views.cache_status'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
    ('^favicon.ico$', 'django.views.generic.simple.redirect_to', {
        'url': '%sfavicon.ico' % settings.STATIC_URL
    }),
    (r'^robots\.txt$', include('robots.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index',
        {'sitemaps': sitemaps.SITEMAPS}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps.SITEMAPS}),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
   )
