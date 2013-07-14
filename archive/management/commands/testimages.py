from django.core.management.base import BaseCommand, CommandError
from archive.tasks.images import get_phantomjs_screenshot
from archive.models import Site, Update
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        help = 'Archive screenshots for all sites'
        update = Update.objects.create(
            start=timezone.now(),
        )
        shit_list = [
            'azcentralcom',
        ]
        for site in Site.objects.filter(slug__in=shit_list):
            get_phantomjs_screenshot.delay(site.id, update.id)
            #get_phantomjs_screenshot(site.id, update.id)
