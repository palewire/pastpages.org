from django.core.management.base import BaseCommand, CommandError
from archive.tasks.images import get_phantomjs_screenshot
from archive.models import Site, Screenshot


class Command(BaseCommand):

    def handle(self, *args, **options): 
        obj = Site.objects.all()[0]
        get_phantomjs_screenshot(
            obj.id
        )
