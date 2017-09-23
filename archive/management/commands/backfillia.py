import logging
from archive.models import Screenshot
from archive.tasks import backfill_to_internet_archive
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backload screenshots to the Internet Archive'

    def add_arguments(self, parser):
        parser.add_argument('count', nargs=1, type=int)

    def handle(self, *args, **options):
        # Query screenshots that are on Rackspace but not IA.
        rackspace_list = Screenshot.objects.rackspace_not_ia()[:options['count'][0]]

        # Loop through the list
        for obj in rackspace_list:
            # Fire up the task to backfill
            backfill_to_internet_archive(obj.id)
