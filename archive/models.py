import os
import logging
from archive import managers
from django.db import models
from django.conf import settings
from bakery.models import BuildableModel
from taggit.managers import TaggableManager
from toolbox.thumbs import ImageWithThumbsField
logger = logging.getLogger(__name__)


class Site(BuildableModel):
    """
    A news website included in the archive.
    """
    detail_views = [
        'archive.views.SiteDetail',
    ]
    
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    url = models.URLField()
    display_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
        default='active')
    y_offset = models.IntegerField(default=0, blank=True)
    on_the_homepage = models.BooleanField(default=True)
    objects = models.Manager()
    tags = TaggableManager(blank=True)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("archive-site-detail", [self.slug])


class Update(BuildableModel):
    """
    A periodic update to the archive.
    """
    detail_views = [
        'archive.views.UpdateDetail',
    ]
    
    start = models.DateTimeField()
    objects = managers.UpdateManager()
    
    class Meta:
        ordering = ('-start',)
        get_latest_by = ("start")
    
    def __unicode__(self):
        return u'%s' % (self.start)
    
    @models.permalink
    def get_absolute_url(self):
        return ("archive-update-detail", [self.id])


def get_image_path(instance, filename):
    return get_screenshot_path(instance, "images", filename)


def get_html_path(instance, filename):
    return get_screenshot_path(instance, "html", filename)


def get_screenshot_path(instance, type, filename):
    return os.path.join('archive', str(instance.update.id),
        instance.site.slug, type, filename)


class Screenshot(BuildableModel):
    """
    A snapshot of web page.
    """
    detail_views = [
        'archive.views.ScreenshotDetail',
    ]
    
    site = models.ForeignKey(Site)
    update = models.ForeignKey(Update)
    timestamp = models.DateTimeField(blank=True, null=True)
    image = ImageWithThumbsField(upload_to=get_image_path, blank=True,
        sizes=((449, 3000),))
    has_image = models.BooleanField(default=False)
    crop = ImageWithThumbsField(upload_to=get_image_path, blank=True,
         sizes=((300, 251),(101, 84)))
    has_crop = models.BooleanField(default=False)
    html_raw = models.FileField(upload_to=get_html_path, blank=True)
    html_archived = models.FileField(upload_to=get_html_path, blank=True)
    has_html = models.BooleanField(default=False)
    
    class Meta:
        ordering = ("-update__start", "site__name")
        unique_together = ("site", "update")
    
    def __unicode__(self):
        return u'%s (%s)' % (self.site, self.update.start)
    
    @models.permalink
    def get_absolute_url(self):
        return ("archive-screenshot-detail", [self.id])
    
    def get_image_name(self):
        return '%s-%s-%s-image.png' % (self.site.slug, self.update.id, self.id)
    
    def get_crop_name(self):
        return '%s-%s-%s-crop.png' % (self.site.slug, self.update.id, self.id)


class Champion(models.Model):
    """
    Someone who has given money to support the site.
    """
    name = models.CharField(max_length=500)
    link = models.URLField(blank=True)
    
    def __unicode__(self):
        return self.name
