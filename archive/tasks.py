from __future__ import absolute_import, unicode_literals
import os
import time
import random
import string
import signal
import shutil
import archiveis
import subprocess
import savepagenow
import webcitation
import internetarchive
from celery import shared_task
from celery.decorators import task
from django.conf import settings
from django.utils import timezone
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


@task()
def backfill_to_internet_archive_batch(obj_id, batch_id):
    """
    Given a screenshot id, this task will backfill all Screenshots
    from the same site and month as a batch item in the Internet Archive.
    """
    obj = Screenshot.objects.get(id=obj_id)
    logger.debug("Backfilling {}".format(obj))
    try:
        obj.upload_screenshot_to_ia_batch(batch_id)
    except Exception as e:
        logger.error(e)
        return

    obj.internetarchive_batch_id = batch_id
    obj.internetarchive_image_url = 'https://archive.org/download/{}/{}'.format(
        obj.internetarchive_batch_id,
        os.path.basename(obj.image.name)
    )
    obj.internetarchive_crop_url = 'https://archive.org/download/{}/{}'.format(
        obj.internetarchive_batch_id,
        os.path.basename(obj.crop.name)
    )
    obj.internetarchive_meta_url = 'https://archive.org/download/{}/{}'.format(
        obj.internetarchive_batch_id,
        obj.ia_screenshot_meta_name
    )
    obj.save()

    logger.debug("Debugging the result")
    logger.debug(obj.ia_batch_url)
    logger.debug(obj.internetarchive_image_url)
    logger.debug(obj.internetarchive_crop_url)
    logger.debug(obj.internetarchive_meta_url)

    print("Sleeping")
    time.sleep(1)

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
