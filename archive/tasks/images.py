# Misc.
import os
import base64
import random
import string
import subprocess
from django.conf import settings
from django.utils import timezone
from celery.decorators import task
from archive.models import Screenshot, Update, Site

# Browser spoofing
from selenium import webdriver
from pyvirtualdisplay import Display

# Timeout tricks
from toolbox.decorators import timeout
from toolbox.decorators import DecoratorTimeoutError
from selenium.common.exceptions import TimeoutException

# Image manipulation
import Image
from toolbox.thumbs import prep_pil_for_db
from django.core.files.base import ContentFile

# Logging
import logging
logger = logging.getLogger(__name__)

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
    Fetch a screenshot using PhantomJS
    """
    # Get the objects we're working with
    site = Site.objects.get(id=site_id)
    update = Update.objects.get(id=update_id)
    # Prepare the parameters for our command line call to PhantomJS
    output_path = os.path.join(
        settings.REPO_DIR,
        '%s.png' % site
    )
    params = [PHANTOM_BIN, PHANTOM_SCRIPT, site.url, output_path]
    # Snap a screenshot of the target site
    logger.debug("Opening %s" % site.url)
    timestamp = timezone.now()
    exitcode = subprocess.call(params)
    # Report back
    if exitcode != 0:
        print "FAILED?: %s" % exitcode
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
    logger.debug("Screenshot saved for %s" % site.url)
    
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
    logger.debug("Crop saved for %s" % site.url)
    
    # Done
    logger.debug("Finished %s" % site.url)


@timeout(45)
def get_safe_screenshot(browser):
    """
    Grab a screenshot from inside Selenium, but timeout if it takes too long.
    """
    return browser.get_screenshot_as_base64()


def get_selenium_screenshot(site_id, update_id):
    """
    Create a screenshot using Selenium and Fire and save it to the database
    """
    # Get the objects we're working with
    site = Site.objects.get(id=site_id)
    update = Update.objects.get(id=update_id)
    
    # Fire up a headless display to work in
    display = Display(visible=0, size=(1680, 1050))
    display.start()
    
    # Fire up a Selenium browsers
    browser = webdriver.Firefox()
    
    # Set a timeout for the pageload
    seconds = 15
    browser.command_executor._commands['setPageLoadTimeout'] = (
        'POST', '/session/$sessionId/timeouts'
    )
    browser.execute("setPageLoadTimeout", {
        'ms': 1000*seconds,
        'type':'page load'
    })
    
    # Snap a screenshot of the target site
    logger.debug("Opening %s" % site.url)
    timestamp = timezone.now()
    try:
        browser.get(site.url + "?x=" + get_random_string())
        logger.debug("Response received for %s" % site.url)
    except TimeoutException, e:
        logger.error("Request for %s timed out" % site.url)
        pass
    except Exception, e:
        # If it fails, close everything out and raise an error
        logger.error("Request for %s failed" % site.url)
        browser.quit()
        display.stop()
        raise e
    
    logger.debug("Screenshotting %s" % site.url)
    try:
        encoded_data = get_safe_screenshot(browser)
        logger.debug("Screenshot retrieved for %s" % site.url)
    except DecoratorTimeoutError, e:
        logger.error("Screenshotting of %s timed out" % site.url)
        browser.quit()
        display.stop()
        raise e
    except Exception, e:
        logger.error("Screenshot failed for %s" % site.url)
        browser.quit()
        display.stop()
        raise e
    
    # Close our browser and faux display
    browser.quit()
    display.stop()
    
    # Convert the screenshot data into something we can save
    decoded_data = base64.decodestring(encoded_data)
    file_obj = ContentFile(decoded_data)
    
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
    logger.debug("Screenshot saved for %s" % site.url)
    
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
    logger.debug("Crop saved for %s" % site.url)
    
    # Building HTML pages
    #logger.debug("Building screenshot detail page for %s" % site.url)
    #ssht.build()
    #logger.debug("Building site detail page for %s" % site.url)
    #site.build()
    
    # Done
    logger.debug("Finished %s" % site.url)
