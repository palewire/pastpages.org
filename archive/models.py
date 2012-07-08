import os
import logging
from archive import managers
from django.db import models
from datetime import datetime
from django.conf import settings
from pytz import common_timezones
from taggit.managers import TaggableManager
from toolbox.thumbs import ImageWithThumbsField
from django.template.defaultfilters import date as dateformat
logger = logging.getLogger(__name__)


class Site(models.Model):
    """
    A news website included in the archive.
    """
    name = models.CharField(help_text='The formal name of the site that will display \
        for users', max_length=150)
    sortable_name = models.CharField(help_text='The version of the name used for sorting',
        max_length=150, blank=True)
    slug = models.SlugField(unique=True)
    url = models.URLField()
    display_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    timezone = models.CharField(max_length=500,
        blank=True, choices=[(i, i) for i in common_timezones],
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
        default='active')
    y_offset = models.IntegerField(default=0, blank=True)
    on_the_homepage = models.BooleanField(default=True)
    objects = managers.SiteManager()
    tags = TaggableManager(blank=True)
    
    class Meta:
        ordering = ('sortable_name', 'name',)
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("archive-site-detail", [self.slug])


class Update(models.Model):
    """
    A periodic update to the archive.
    """
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


class Screenshot(models.Model):
    """
    A snapshot of web page.
    """
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
        ordering = ("-update__start", "site__sortable_name", "site__name")
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
    
    def get_mla_citation(self):
        """
        The proper way to cite a screenshot in MLA style.
        """
        style = '"%(title)s." <em>PastPages</em>. %(creation_date)s. Web. %(today)s. &lt;%(url)s&gt;'
        data = dict(
            title = "%s homepage at %s" % (self.site.name, dateformat(self.timestamp, 'N j, Y, P e')),
            creation_date = dateformat(self.timestamp, 'j N Y'),
            today = dateformat(datetime.now().today(), 'j N Y'),
            url = "http://www.pastpages.org%s" % self.get_absolute_url(),
        )
        return style % data
    mla_citation = property(get_mla_citation)
    
    def get_apa_citation(self):
        """
        The proper way to cite a screenshot in APA style.
        """
        style = '%(title)s. (%(creation_date)s). <em>PastPages</em>. Retrieved from %(url)s'
        data = dict(
            title = "%s homepage at %s" % (self.site.name, dateformat(self.timestamp, 'N j, Y, P e')),
            creation_date = dateformat(self.timestamp, 'Y, N j'),
            url = "http://www.pastpages.org%s" % self.get_absolute_url(),
        )
        return style % data
    apa_citation = property(get_apa_citation)
    
    def get_chicago_citation(self):
        """
        The proper way to cite a screenshot in Chicago style.
        """
        style = '"%(title)s." PastPages. Last modified %(creation_date)s, %(url)s.'
        data = dict(
            title = "%s homepage at %s" % (self.site.name, dateformat(self.timestamp, 'N j, Y, P e')),
            creation_date = dateformat(self.timestamp, 'F j, Y'),
            url = "http://www.pastpages.org%s" % self.get_absolute_url(),
        )
        return style % data
    chicago_citation = property(get_chicago_citation)
    
    def get_wikipedia_citation(self):
        """
        The proper way to cite a screenshot in Wikipedia markup.
        """
        style = """{{cite web<br>
         &nbsp;&nbsp;&nbsp;&nbsp;| url = %(url)s<br>
         &nbsp;&nbsp;&nbsp;&nbsp;| title = %(title)s<br>
         &nbsp;&nbsp;&nbsp;&nbsp;| publisher = PastPages<br>
         &nbsp;&nbsp;&nbsp;&nbsp;| date = %(creation_date)s<br>
         &nbsp;&nbsp;&nbsp;&nbsp;| accessdate = %(today)s<br>
         &nbsp;&nbsp;&nbsp;&nbsp;| ref = {{harvid|PastPages-%(id)s|%(year)s}}<br>
        }}"""
        data = dict(
            title = "%s homepage at %s" % (self.site.name, dateformat(self.timestamp, 'N j, Y, P e')),
            creation_date = dateformat(self.timestamp, 'N j, Y'),
            today = dateformat(datetime.now().today(), 'N j, Y'),
            url = "http://www.pastpages.org%s" % self.get_absolute_url(),
            year = dateformat(self.timestamp, 'Y'),
            id = str(self.id),
        )
        return style % data
    wikipedia_citation = property(get_wikipedia_citation)


class Champion(models.Model):
    """
    Someone who has given money to support the site.
    """
    name = models.CharField(max_length=500)
    link = models.URLField(blank=True)
    
    def __unicode__(self):
        return self.name
