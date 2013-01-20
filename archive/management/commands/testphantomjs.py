from django.core.management.base import BaseCommand, CommandError
from archive.tasks.images import get_phantomjs_screenshot
from archive.models import Site, Update
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options): 
        update = Update.objects.create(
            start=timezone.now(),
        )
        for site in Site.objects.active():
            get_phantomjs_screenshot.delay(site.id, update.id)
