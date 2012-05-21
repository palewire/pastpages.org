from django.core.management.base import BaseCommand, CommandError
from archive.tasks import get_html
from archive.models import Site, Screenshot


class Command(BaseCommand):

    def handle(self, *args, **options): 
        obj = Site.objects.get(name="Yahoo!")
        get_html(Screenshot.objects.filter(site=obj)[0].id)
