# Misc.
import os
import random
import string
import signal
import subprocess
from django.conf import settings
from django.utils import timezone
from celery.decorators import task
from toolbox.decorators import timeout
from archive.models import Screenshot, Update, Site

# Image manipulation
import Image
import cStringIO
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


@timeout(seconds=60)
def run_phantom_js(params):
    exitcode = subprocess.call(params)
    return exitcode


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
        '%s.jpg' % site.slug
    )
    url = '%s?random=%s' % (site.url, get_random_string())
    params = [PHANTOM_BIN, PHANTOM_SCRIPT, url, output_path]
    
    # Snap a screenshot of the target site
    logger.debug("Opening %s" % site.url)
    timestamp = timezone.now()
    
    try:
        exitcode = run_phantom_js(params)
    except:
        logger.error("Phantom JS timeout: %s" % site)
        cmd = "ps -ef | grep phantomjs | grep %s | grep -v grep | awk '{print $2}'" % site.slug
        logger.error(cmd)
        output = subprocess.check_output([cmd], shell=True)
        if output:
            pid_list = output.split()
            for pid in pid_list:
                logger.error("Killing PID %s" % pid)
                os.kill(int(pid), signal.SIGKILL)
        return False
    
    # Report back
    if exitcode != 0:
        logger.error("FAILED?: %s" % exitcode)
        return False
    
    # Read the image file into memory
    data = open(output_path, 'r').read()
    
    # Convert the data to a Django object
    jpg_obj = ContentFile(data)
    
    # Remove the image from the local filesystem
    os.remove(output_path)
    
    # Create a screenshot object in the database
    ssht, created = Screenshot.objects.get_or_create(site=site, update=update)
    
    # Save the image data to the object
    target = ssht.get_image_name()
    try:
        ssht.image.save(target, jpg_obj)
    except Exception, e:
        logger.error("Image save failed.")
        logger.error(str(e))
        ssht.delete()
        return False
    ssht.has_image = True
    ssht.timestamp = timestamp
    ssht.save()
    
    # Reopen image as PIL object
    jpg_obj.seek(0)
    image = Image.open(jpg_obj)
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
        logger.error(str(e))
        ssht.delete()
        return False
    ssht.has_crop = True
    ssht.save()
    
    if site.has_html_screenshots:
        logger.info("Logging HTML for %s" % site.url)
        ssht.html = site.url
        ssht.has_html = True
        ssht.save()

    # Finish
    logger.debug("Finished %s" % site)
