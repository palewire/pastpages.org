import logging
from django.conf import settings
from archive.models import Screenshot
from internetarchive import upload, get_item, get_files
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test uploading a screenshot to the Internet Archive'

    def handle(self, *args, **options):
        uid = 'drudge-report-45135-3477691-foobar'
        i, c = self.get_or_create_ia_item(uid)
        print i, c
        print i.metadata
        print list(i.get_files(formats="JPEG"))[0].url
