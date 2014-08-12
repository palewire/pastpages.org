from django.core.management.base import BaseCommand
from archive.tasks import get_phantomjs_screenshot
from archive.models import Site, Update
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Archive screenshots for all sites'

    def handle(self, *args, **options):
        update = Update.objects.create(
            start=timezone.now(),
        )
        shit_list = [
            'chicago-tribune',
        ]
        for site in Site.objects.filter(slug__in=shit_list):
            #get_phantomjs_screenshot.delay(site.id, update.id)
            get_phantomjs_screenshot(site.id, update.id)
