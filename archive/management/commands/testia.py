import logging
from django.conf import settings
from archive.models import Screenshot
from internetarchive import upload, get_item, get_files
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test uploading a screenshot to the Internet Archive'

    def upload_ia_item(self, uid):
        md = dict(
            collection="pastpages",
            title='Drudge Report archived on Tuesday Aug. 8, 2017 at 4:03 a.m. UTC',
            mediatype='image',
            contributor="pastpages.org",
            creator="pastpages.org",
            publisher=None,
            date=None,
            pastpages_id="3477691",
            pastpages_url="http://www.pastpages.org/screenshot/3477691/",
            pastpages_timestamp=None,
            pastpages_site_id=None,
            pastpages_update_id=None,
        )
        upload(
            uid,
            files=['./drudge-report-45135-3477691-image.jpg',],
            metadata=md,
            access_key=settings.IA_ACCESS_KEY_ID,
            secret_key=settings.IA_SECRET_ACCESS_KEY,
        )
        return get_item(uid)

    def get_ia_item(self, uid):
        config = dict(s3=dict(access=settings.IA_ACCESS_KEY_ID, secret=settings.IA_SECRET_ACCESS_KEY))
        return get_item(uid, config=config)

    def get_or_create_ia_item(self, uid):
        i = self.get_ia_item(uid)
        if i.exists:
            return i, False
        else:
            return self.upload_ia_item(uid), True

    def handle(self, *args, **options):
        uid = 'drudge-report-45135-3477691-foobar'
        i, c = self.get_or_create_ia_item(uid)
        print i, c
        print i.metadata
        print list(i.get_files(formats="JPEG"))[0].url
