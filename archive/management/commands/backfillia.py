import logging
from django.conf import settings
from archive.models import Screenshot
from internetarchive import upload, get_item, get_files
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backload screenshots to the Internet Archive'

    def add_arguments(self, parser):
        parser.add_argument('count', nargs=1, type=int)

    def handle(self, *args, **options):
        rackspace_list = Screenshot.objects.rackspace_not_ia()[:options['count'][0]]
        for obj in rackspace_list:
            obj.sync_with_ia()

            logger.debug("Deleting Rackspace images for {}".format(obj))
            if obj.has_image:
                logger.debug("Deleting {}".format(obj.image))
                obj.image.delete()
                obj.has_image = False
            if obj.has_crop:
                logger.debug("Deleting {}".format(obj.crop))
                obj.crop.delete()
                obj.has_crop = False

            logger.debug("Resaving {}".format(obj))
            obj.save()
