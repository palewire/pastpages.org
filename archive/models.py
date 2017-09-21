import os
import logging
import internetarchive
from archive import managers
from django.db import models
from datetime import datetime
from django.conf import settings
from pytz import common_timezones
from taggit.managers import TaggableManager
from django.core.files.base import ContentFile
from toolbox.thumbs import ImageWithThumbsField
from urlarchivefield.fields import URLArchiveField
from django.template.defaultfilters import date as dateformat
logger = logging.getLogger(__name__)


class Site(models.Model):
    """
    A news website included in the archive.
    """
    name = models.CharField(
        help_text='The formal name of the site that will display for users',
        max_length=150
    )
    sortable_name = models.CharField(
        help_text='The version of the name used for sorting',
        max_length=150
    )
    slug = models.SlugField(unique=True)
    url = models.URLField()
    display_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    hometown = models.CharField(max_length=500, blank=True)
    timezone = models.CharField(
        max_length=500,
        blank=True,
        choices=[(i, i) for i in common_timezones],
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
    )
    on_the_homepage = models.BooleanField(default=True)

    # Local screenshots
    has_html_screenshots = models.BooleanField(default=False)
    y_offset = models.IntegerField(default=0, blank=True)

    # Third party mementos
    has_internetarchive_mementos = models.BooleanField(
        verbose_name='has Internet Archive mementos',
        default=False
    )
    has_archiveis_mementos = models.BooleanField(
        verbose_name='has archive.is mementos',
        default=False
    )
    has_webcitation_mementos = models.BooleanField(
        verbose_name="has webcitation.org mementos",
        default=False
    )

    # Managers
    objects = managers.SiteManager()
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ('sortable_name', 'name',)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("archive-site-detail", [self.slug])

    @models.permalink
    def get_timemap_index_url(self):
        return ("timemap-url-link-feed", [], dict(url=self.url))


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
    return os.path.join(
        'archive',
        str(instance.update.id),
        instance.site.slug,
        type,
        filename
    )



class Memento(models.Model):
    """
    A snapshot of a web page stored by a third-party archive at our request.
    """
    # Basics
    site = models.ForeignKey(Site)
    update = models.ForeignKey(Update)
    timestamp = models.DateTimeField(
        db_index=True,
        auto_now_add=True,
    )
    ARCHIVE_CHOICES = (
        ('archive.org', 'archive.org'),
        ('archive.is', 'archive.is'),
        ('webcitation.org', 'webcitation.org'),
    )
    archive = models.CharField(
        max_length=1000,
        choices=ARCHIVE_CHOICES,
        db_index=True,
    )
    url = models.URLField(blank=True)

    class Meta:
        ordering = ("-update__start", "site__sortable_name", "site__name")
        unique_together = ("site", "update", "archive")
        index_together = [
            ["site", "archive",],
        ]

    def __unicode__(self):
        return u'%s (%s) at %s' % (self.site, self.update.start, self.archive)


class Screenshot(models.Model):
    """
    A snapshot of web page.
    """
    site = models.ForeignKey(Site)
    update = models.ForeignKey(Update)
    timestamp = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True
    )
    image = ImageWithThumbsField(
        upload_to=get_image_path,
        blank=True,
        sizes=((449, 3000),)
    )
    has_image = models.BooleanField(default=False, db_index=True)
    crop = ImageWithThumbsField(
        upload_to=get_image_path,
        blank=True,
        sizes=((300, 251),)
    )
    has_crop = models.BooleanField(default=False, db_index=True)
    html = URLArchiveField(upload_to=get_html_path)
    has_html = models.BooleanField(default=False)

    # Internet Archive assets
    internetarchive_id = models.CharField(max_length=5000, blank=True)
    internetarchive_image_url = models.CharField(max_length=5000, blank=True)
    internetarchive_crop_url = models.CharField(max_length=5000, blank=True)

    class Meta:
        ordering = ("-update__start", "site__sortable_name", "site__name")
        unique_together = ("site", "update",)
        index_together = [
            ["site", "has_image", "has_crop"],
        ]
        get_latest_by = 'timestamp'

    def __unicode__(self):
        return u'%s (%s)' % (self.site, self.update.start)

    @models.permalink
    def get_absolute_url(self):
        return ("archive-screenshot-detail", [self.id])

    def get_image_name(self):
        return '%s-%s-%s-image.jpg' % (self.site.slug, self.update.id, self.id)

    def get_crop_name(self):
        return '%s-%s-%s-crop.jpg' % (self.site.slug, self.update.id, self.id)

    #
    # Internet Archive
    #

    @property
    def ia_id(self):
        return "pastpages-{}-{}-{}".format(self.site.slug, self.update_id, self.id)

    def save_image(self):
        name = os.path.basename(self.image.name)
        with open(name, 'wb') as f:
            f.write(self.image.file.file.read())
        return name

    def save_crop(self):
        name = os.path.basename(self.crop.name)
        with open(name, 'wb') as f:
            f.write(self.crop.file.file.read())
        return name

    def upload_ia_item(self):
        logger.debug("Uploading IA item for {}".format(self.ia_id))
        metadata = dict(
            collection="pastpages",
            title='{} at {}'.format(self.site.name, dateformat(self.timestamp, 'N j, Y, P')),
            mediatype='image',
            contributor="pastpages.org",
            creator="pastpages.org",
            publisher=self.site.name,
            date=str(self.timestamp),
            subject=["news", "homepages", "screenshot"],
            pastpages_id=self.id,
            pastpages_url=self.get_absolute_url(),
            pastpages_timestamp=str(self.timestamp),
            pastpages_site_id=self.site.id,
            pastpages_site_slug=self.site.slug,
            pastpages_update_id=self.update.id,
        )
        files = []
        if self.has_image:
            saved_image = self.save_image()
            files.append(saved_image)
        if self.has_crop:
            saved_crop = self.save_crop()
            files.append(saved_crop)
        internetarchive.upload(
            self.ia_id,
            files,
            metadata=metadata,
            access_key=settings.IA_ACCESS_KEY_ID,
            secret_key=settings.IA_SECRET_ACCESS_KEY,
            checksum=False,
            verbose=True
        )
        if self.has_image:
            os.remove(saved_image)
        if self.has_crop:
            os.remove(saved_crop)
        return internetarchive.get_item(self.ia_id)

    def get_ia_item(self):
        logger.debug("Getting IA item for {}".format(self.ia_id))
        config = dict(s3=dict(access=settings.IA_ACCESS_KEY_ID, secret=settings.IA_SECRET_ACCESS_KEY))
        return internetarchive.get_item(self.ia_id, config=config)

    def get_or_create_ia_item(self):
        i = self.get_ia_item()
        if i.exists:
            logger.debug("IA item for {} exists".format(self.ia_id))
            return i, False
        else:
            logger.debug("IA item for {} does not exist".format(self.ia_id))
            return self.upload_ia_item(), True

    def sync_with_ia(self):
        logger.debug("Syncing IA item for {}".format(self.ia_id))
        item, created = self.get_or_create_ia_item()
        try:
            image_url = [x for x in list(item.get_files(formats="JPEG")) if 'image' in x.name][0].url
            self.internetarchive_image_url = image_url
        except IndexError:
            self.internetarchive_image_url = ''
        try:
            crop_url = [x for x in list(item.get_files(formats="JPEG")) if 'crop' in x.name][0].url
            self.internetarchive_crop_url = crop_url
        except IndexError:
            self.internetarchive_crop_url = ''
        self.internetarchive_id = item.identifier
        self.save()

    #
    # Citations
    #

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


class ScreenshotLog(models.Model):
    """
    A log entry made while saving a screenshot.
    """
    update = models.ForeignKey(Update)
    site = models.ForeignKey(Site)
    screenshot = models.ForeignKey(Screenshot, null=True)
    MESSAGE_TYPE_CHOICES = (
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('error', 'Error'),
    )
    message_type = models.CharField(
        choices=MESSAGE_TYPE_CHOICES,
        max_length=100,
    )
    message = models.TextField()

    def __unicode__(self):
        return self.message
