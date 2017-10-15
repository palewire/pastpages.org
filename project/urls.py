from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from archive import views, sitemaps, feeds
from django.views.static import serve as static_serve
from django.contrib.sitemaps import views as sitemap_views
from django.views.generic import TemplateView, RedirectView
from django.contrib.admin.views.decorators import staff_member_required
admin.autodiscover()

urlpatterns = [

#    url(r'^(.*)$', views.Fail.as_view(),
#        name='archive-fail'),

    # Pages for humans
    url(r'^$', views.Index.as_view(),
        name='archive-index'),
    url(r'^about/$', views.AboutDetail.as_view(),
        name='about'),
    url(r'^champions/$', views.ChampionsList.as_view(),
        name='champions'),
    url(r'^site/(?P<slug>[-\w]+)/$', views.SiteDetail.as_view(),
        name='archive-site-detail'),
    url(r'^tag/(?P<slug>[-\w]+)/$', views.TagDetail.as_view(),
        name='archive-tag-detail'),
    url(r'^update/(?P<pk>\d+)/$', views.UpdateDetail.as_view(),
        name='archive-update-detail'),
    url(r'^screenshot/(?P<pk>\d+)/$', views.ScreenshotDetail.as_view(),
        name='archive-screenshot-detail'),
    url(r'^screenshot/(?P<pk>\d+)/hyperlinks-csv/$',
        views.ScreenshotDetailHyperlinksCSV.as_view(),
        name='archive-screenshot-detail-hyperlinks-csv'),
    url(r'^advanced-search/$', views.AdvancedSearch.as_view(),
        name='archive-advanced-search'),
    url(r'^contact/$', TemplateView.as_view(template_name='contact.html'),
        name='contact'),

    # Pages for machines
    url(r'^sitemap\.xml$', sitemap_views.index, {'sitemaps': sitemaps.SITEMAPS}),
    url(
        r'^sitemap-(?P<section>.+)\.xml$',
        sitemap_views.sitemap,
        {'sitemaps': sitemaps.SITEMAPS},
        name='django.contrib.sitemaps.views.sitemap'
    ),

    url('^favicon.ico$', RedirectView.as_view(
        url='%sfavicon.ico' % settings.STATIC_URL
        )),

    url(r'^robots\.txt', include('robots.urls')),

    url(r'^api/', include('api.urls')),
    url(
        r'^api/docs/',
        TemplateView.as_view(template_name='api_docs.html'),
        name='api-docs'
    ),

    url(r'^feeds/$', views.FeedList.as_view(), name='feeds-list'),
    url(r'^feeds/updates/$', feeds.RecentUpdates(), name="feeds-updates"),
    url(
        r'^feeds/sites/(?P<slug>[-\w]+)/$',
        feeds.SiteFeed(),
        name="feeds-sites"
    ),
    url(
        r'^feeds/tags/(?P<slug>[-\w]+)/$',
        feeds.TagFeed(),
        name="feeds-tags"
    ),

    # Memento
    url(
        r'^timemap/link/(?P<url>.*)$',
        feeds.SiteTimemapLinkList(),
        name="timemap-url-link-feed"
    ),
    url(
        r'^timegate/(?P<url>.*)$',
        views.ScreenshotTimeGate.as_view(),
        name="timegate-screenshot"
    ),

    # Monitoring and administration
    url(r'^admin/', admin.site.urls),
    url(r'^status/$', views.Status.as_view(), name='status'),
]

# Pages for developers
if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', static_serve, {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True,
        }),
   ]
