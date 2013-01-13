from django.core.management.base import BaseCommand, CommandError
from archive.tasks.images import get_phantomjs_screenshot
from archive.models import Site, Update
from django.utils import timezone


class Command(BaseCommand):

    def handle(self, *args, **options): 
        obj = Site.objects.all().order_by("?")[0]
        update = Update.objects.create(
            start=timezone.now(),
        )
        get_phantomjs_screenshot(
            obj.id,
            update.id
        )
