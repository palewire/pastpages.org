import logging
from archive import feeds
from pprint import pprint
from django.db import connection
from django.test import RequestFactory
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Initialize our timemap view and database logic
        timemap = feeds.SiteTimemapLinkList()
        # Create a simulated web request
        factory = RequestFactory()
        request = factory.get(
            "/timemap/link/http://www.cnn.com/?page=44",
            page=44
        )
        # Pass the fake web request to the timemap view
        response = timemap(request, url="http://www.cnn.com/")
        # Print out the HTTP response content
        print response
        # Print out the number of database queries
        print "%s queries" % len(connection.queries)
        # Print out the individual queries
        pprint(connection.queries)
