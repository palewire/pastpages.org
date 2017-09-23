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
from celery.decorators import task
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

# PhantomJS bits we'll use for screenshots
PHANTOM_BIN = os.path.join(
    settings.REPO_DIR, 'phantomjs', 'bin', 'phantomjs'
)
PHANTOM_SCRIPT = os.path.join(
    settings.REPO_DIR, 'archive', 'tasks', 'images.js'
)


def get_random_string(length=6):
    """
    Generate a random string of letters and numbers
    """
    return ''.join(
        random.choice(string.letters + string.digits) for i in xrange(length)
    )


@timeout(seconds=80)
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
        ScreenshotLog.objects.create(
            update=update,
            site=site,
            message_type="error",
            message="Phantom JS timeout"
        )
        cmd = "ps -ef | grep phantomjs | grep %s | grep -v grep \
| awk '{print $2}'" % site.slug
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
        ScreenshotLog.objects.create(
            update=update,
            site=site,
            message_type="error",
            message="Failed with exitcode %s" % exitcode
        )
        return False

    # Read the image file into memory
    try:
        data = open(output_path, 'r').read()
    except IOError, e:
        logger.error("IOError: %s" % e)
        ScreenshotLog.objects.create(
            update=update,
            site=site,
            message_type="error",
            message="IOError: %s" % e
        )
        return False

    # Convert the data to a Django object
    jpg_obj = ContentFile(data)

    # Create a screenshot object
    logger.debug("Creating Screenshot object for {}-{}".format(site, update))
    ssht, created = Screenshot.objects.get_or_create(site=site, update=update)
    ssht.timestamp = timestamp

    # Open up the image
    jpg_obj.seek(0)
    image = Image.open(jpg_obj)
    width = image.width

    # Crop it to 1000px tall, starting from the top
    crop = image.crop(
        (
            0,
            # Unless we provide an offset to scroll down before cropping
            getattr(ssht.site, "y_offset", 0),
            width,
            1000
        )
    )

    # Move the original file to Internet Archive namespace
    shutil.copy(output_path, ssht.get_image_name())

    # Save crop to Internet Archive namespace
    crop.save(open(ssht.get_crop_name(), 'w'))

    # Upload both images to Internet Archive
    files = [ssht.get_image_name(), ssht.get_crop_name()]
    try:
        logger.debug("Uploading to internetarchive as {}".format(ssht.ia_id))
        internetarchive.upload(
            ssht.ia_id,
            files,
            metadata=ssht.ia_metadata,
            access_key=settings.IA_ACCESS_KEY_ID,
            secret_key=settings.IA_SECRET_ACCESS_KEY,
            checksum=False,
            verbose=True
        )
    except Exception, e:
        logger.error("internetarchive error: %s" % e)
        ScreenshotLog.objects.create(
            update=update,
            site=site,
            message_type="error",
            message="internetarchive error: %s" % e
        )
        ssht.delete()
        return False

    # Retreive item from IA
    item = ssht.get_ia_item()

    # Create screenshot object with Internet Archive link
    ssht.internetarchive_id = item.identifier
    logger.debug("Setting internetarchive_id as {}".format(item.identifier))

    # Save again
    ssht.save()

    # Remove images from the local filesystem
    [os.remove(f) for f in files]

    # Internet Archive mementos where turned on
    if site.has_internetarchive_mementos:
        logger.info("Adding archive.org memento for %s" % site.url)
        try:
            ia_memento, ia_created = savepagenow.capture_or_cache(
                site.url,
                user_agent="pastpages.org (ben.welsh@gmail.com)"
            )
            if ia_created:
                memento = Memento.objects.create(
                    site=site,
                    update=update,
                    archive='archive.org',
                    url=ia_memento,
                )
            else:
                logger.info("Internet Archive returned a cached memento")
        except Exception:
            logger.info("Adding Internet Archive memento failed")

    # Archive.is mementos where turned on
    if site.has_archiveis_mementos:
        logger.info("Adding archive.is memento for %s" % site.url)
        try:
            is_memento = archiveis.capture(
                site.url,
                user_agent="pastpages.org (ben.welsh@gmail.com)"
            )
            is_created = Memento.objects.filter(url=is_memento).count() == 0
            if is_created:
                memento = Memento.objects.create(
                    site=site,
                    update=update,
                    archive='archive.is',
                    url=is_memento,
                )
            else:
                logger.info("archive.is returned a cached memento")
        except Exception:
            logger.info("Adding archive.is memento failed")

    # webcitation mementos where turned on
    if site.has_webcitation_mementos:
        logger.info("Adding webcitation.org memento for %s" % site.url)
        try:
            wc_memento = webcitation.capture(
                site.url,
                user_agent="pastpages.org (ben.welsh@gmail.com)"
            )
            memento = Memento.objects.create(
                site=site,
                update=update,
                archive='webcitation.org',
                url=wc_memento,
            )
        except Exception:
            logger.info("Adding webcitation memento failed")

    # Finish
    logger.debug("Finished %s" % site)
