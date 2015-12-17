import logging
from archive import feeds
from pprint import pprint
from django.db import connection
from django.test import RequestFactory
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        timemap = feeds.SiteTimemapLinkList()
        factory = RequestFactory()
        request = factory.get("/timemap/link/http://www.cnn.com/?page=10", page=10)
        response = timemap(request, url="http://www.cnn.com/")
        print response
        print "%s queries" % len(connection.queries)
        pprint(connection.queries)
