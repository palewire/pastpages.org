# Misc.
import os
import random
import string
import subprocess
from django.conf import settings
from django.utils import timezone
from celery.decorators import task
from archive.models import Screenshot, Update, Site

# Image manipulation
import Image
from toolbox.thumbs import prep_pil_for_db
from django.core.files.base import ContentFile

# Logging
import logging
logger = logging.getLogger(__name__)

# PhantomJS bits we'll use for screenshots
PHANTOM_BIN = os.path.join(settings.REPO_DIR, 'phantomjs', 'bin', 'phantomjs')
PHANTOM_SCRIPT = os.path.join(settings.REPO_DIR, 'archive', 'tasks', 'images.js')


def get_random_string(length=6):
    """
    Generate a random string of letters and numbers
    """
    return ''.join(random.choice(string.letters + string.digits) for i in xrange(length))


@task()
def get_phantomjs_screenshot(site_id, update_id):
    """
    Fetch and save a screenshot using PhantomJS.
    """
    # Get the objects we're working with
    site = Site.objects.get(id=site_id)
    update = Update.objects.get(id=update_id)
    
    # Prepare the parameters for our command line call to PhantomJS
    output_path = os.path.join(
        settings.REPO_DIR,
        '%s.png' % site
    )
    url = '%s?random=%s' % (site.url, get_random_string())
    params = [PHANTOM_BIN, PHANTOM_SCRIPT, url, output_path]
    
    # Snap a screenshot of the target site
    logger.debug("Opening %s" % site.url)
    timestamp = timezone.now()
    exitcode = subprocess.call(params)
    
    # Report back
    if exitcode != 0:
        logger.error("FAILED?: %s" % exitcode)
        return False
    
    # Convert the screenshot data into something we can save
    data = open(output_path, 'r').read()
    os.remove(output_path)
    file_obj = ContentFile(data)
    
    # Create a screenshot object in the database
    ssht, created = Screenshot.objects.get_or_create(site=site, update=update)
    
    # Save the image data to the object
    target = ssht.get_image_name()
    logger.debug("Saving %s" % target)
    try:
        ssht.image.save(target, file_obj)
    except Exception, e:
        logger.error("Image save failed.")
        ssht.delete()
        raise e
    ssht.has_image = True
    ssht.timestamp = timestamp
    ssht.save()
    
    # Reopen image as PIL object
    file_obj.seek(0)
    image = Image.open(file_obj)
    # Crop it to 1000px tall, starting from the top
    crop = image.crop(
        (
            0,
             # Unless we provide an offset to scroll down before cropping
            getattr(ssht.site, "y_offset", 0),
            ssht.image.width,
            1000
        )
    )
    # Prep for db
    crop_name = ssht.get_crop_name()
    crop_data = prep_pil_for_db(crop, crop_name)
    # Save to the database
    try:
        ssht.crop.save(crop_name, crop_data)
    except Exception, e:
        logger.error("Crop save failed.")
        ssht.delete()
        raise e
    ssht.has_crop = True
    ssht.save()
    
    # Finish
    logger.debug("Finished %s" % site)
