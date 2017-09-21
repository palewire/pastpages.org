import logging
from django.conf import settings
from archive.models import Screenshot
from internetarchive import upload, get_item, get_files
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test uploading a screenshot to the Internet Archive'

    def handle(self, *args, **options):
        obj = Screenshot.objects.get(id=3512123)
        # print obj.crop.read()
        obj.sync_with_ia()
