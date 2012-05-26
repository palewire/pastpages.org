import logging
from archive import views
from archive.tasks import images
from optparse import make_option
from django.utils import timezone
from django.core import management
logger = logging.getLogger(__name__)
from archive.models import Update, Site
from django.core.management.base import BaseCommand, CommandError


custom_options = (
    make_option(
        "--publish",
        action="store_true",
        dest="publish",
        default=False,
        help="Build and publish results to S3"
    ),
)


class Command(BaseCommand):
    help = 'Archive screenshots for all sites'
    option_list = BaseCommand.option_list + custom_options
    cmd = "s3cmd put --acl-public %(source)s s3://%(target)s"

    def handle(self, *args, **options): 
        update = Update.objects.create(
            start=timezone.now(),
        )
        for site in Site.objects.active():
            try:
                images.get_screenshot(site.id, update.id)
            except Exception, e:
                logger.error(e)
        if options.get("publish"):
             logger.debug("Publishing data to S3")
             views.Index().build_method()
             update.build()
             views.DateDetail().build_object(timezone.localtime(update.start).date())
             views.TagDetail().build_method()
             views.CryForHelp().build_method()
             management.call_command("publish", interactive=False, verbosity=0)
             logger.debug("Finished")


