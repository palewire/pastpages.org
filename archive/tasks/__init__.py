# Misc.
import os
import random
import string
import signal
import shutil
import archiveis
import subprocess
import savepagenow
import webcitation
import internetarchive
from django.conf import settings
from django.utils import timezone
# from celery.decorators import task
from toolbox.decorators import timeout
from archive.models import Screenshot, Update, Site, ScreenshotLog, Memento

# Image manipulation
from PIL import Image
from django.core.files import File
from toolbox.thumbs import prep_pil_for_db
from django.core.files.base import ContentFile

# Logging
import logging
logger = logging.getLogger(__name__)


def get_random_string(length=6):
    """
    Generate a random string of letters and numbers
    """
    return ''.join(
        random.choice(string.letters + string.digits) for i in xrange(length)
    )


# @task()
def backfill_to_internet_archive(screenshot_id):
    # Get the object
    obj = Screenshot.objects.get(id=screenshot_id)

    # Back up the Rackspace images on Internet Archive
    obj.sync_with_ia()

    # Delete the Rackspace images
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
