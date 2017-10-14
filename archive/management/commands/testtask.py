import logging
from archive import tasks
from django.conf import settings
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        tasks.add.delay(2, 2)
