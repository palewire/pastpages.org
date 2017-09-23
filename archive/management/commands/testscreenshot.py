from django.core.management.base import BaseCommand
from archive.tasks import get_phantomjs_screenshot
from archive.models import Site, Update
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Archive screenshots for a white list of sites'

    def handle(self, *args, **options):
        update = Update.objects.create(
            start=timezone.now(),
        )
        shit_list = [
            'drudge-report',
            #'cnn',
            #'new-york-times',
        ]
        for site in Site.objects.filter(slug__in=shit_list):
            #get_phantomjs_screenshot.delay(site.id, update.id)
            get_phantomjs_screenshot(site.id, update.id)

        # from PIL import Image
        # from django.core.files import File
        # from archive.models import Screenshot
        #
        # crop_path = "./crop.jpg"
        # crop_data = File(open(crop_path, 'r'))
        # ssht = Screenshot.objects.filter(site__slug='cnn').latest('timestamp')
        # ssht.crop.save('crop.jpg', crop_data)
