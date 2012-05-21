import os
import re
import sys
import Image
import urllib
import hashlib
import StringIO
import base64
import logging
import random
import string
from django.utils import timezone
from toolbox.decorators import timeout
from toolbox.thumbs import prep_pil_for_db
from copy import copy
from urlparse import urlparse
from django.conf import settings
from archive.models import Screenshot, Update, Site
from BeautifulSoup import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
logger = logging.getLogger(__name__)


def get_html(screenshot_id):
    """
    Visits a site and archives the html, images and styles.
    
    Returns a list of dictionaries. They is the file name, the value
    is the file object ready to be saved.
    """
    screenshot = Screenshot.objects.get(id=screenshot_id)
    url = screenshot.site.url
    
    # Set the path for these files
    html_path = os.path.join(
        settings.SCREENSHOT_PATH,
        str(screenshot.update.id),
        screenshot.site.slug,
        'html',
    )
    
    # Create the directory if it doesn't already exist
    if not os.path.exists(html_path):
        os.makedirs(html_path)
        os.makedirs(os.path.join(html_path, 'media'))

    # Visit the URL and snatch the HTML
    http = urllib.urlopen(url)
    html = http.read()
    original_html = copy(html)
    soup = BeautifulSoup(html)
    
    # A list of all the other resources in the page we need to pull out
    target_list = (
        # images
        {"tag": ("img", {"src": True}), "attr": "src"},
        # css
        {"tag": ("link", {"rel": "stylesheet"}), "attr": "href"},
        # css
        {"tag": ("link", {"rel": "alternate stylesheet", "type": "text/css"}), "attr": "href"},
        # javascript
        {"tag": ("script", {"src": True}), "attr": "src"},
    )
    
    def _archive_file(link):
        file_name = urlparse(link).path
        # Change the file name to a hash so they we can keep the
        # names from getting too long.
        try:
            file_name, file_type = os.path.splitext(file_name)
            if not file_type:
                return None
            hash_name = "%s%s" % (
                hashlib.md5(file_name).hexdigest(),
                file_type
            )
        except:
            hash_name = hashlib.md5(file_name).hexdigest()
        archive_link = "media/%s" % hash_name
        # Add the domain to any relative urls so we know what to fetch.
        # But also strip off that leading slash on the local link.
        if link[0] == '/':
            link = url + link
        try:
            #print "Fetching %s" % link
            # Fetch the data
            http = urllib.urlopen(link)
            data = http.read()
            if link[-4:] == '.css':
                this_list = re.findall("url\((.*)\)", data)
                this_list = [i.replace("'", "").replace('"', "") for i in this_list]
                for this in this_list:
                    # Clear out any CSS crap that comes after the URL,
                    # which is often started with a "}"
                    this = this.split(")")[0]
                    # Straighten out any relative urls that start with ".."
                    if this.startswith("../"):
                        this = "/".join(link.split("/")[:-1]) + "/" + this
                    # Do the bizness
                    this_archive = _archive_file(this)
                    if this_archive:
                        data = data.replace(str(this), str(this_archive).replace("media/", ""))
            tempfile_io = StringIO.StringIO(data)
            # Write out the file
            file_path = os.path.join(html_path, archive_link)
            outfile = open(file_path, "w")
            outfile.write(tempfile_io.read())
            outfile.close()
            return archive_link
        except:
            return None

    # Walk through the html and grab them all
    link_list = []
    for target in target_list:
        for hit in soup.findAll(*target['tag']):
            link = hit.get(target['attr'])
            if not link:
                continue
            archive_link = _archive_file(link)
            if archive_link:
                html = html.replace(str(link), str(archive_link))

    # Save the index file
    screenshot.html_archived.save("index.html", InMemoryUploadedFile(
        StringIO.StringIO(html),
        None,
        "index.html",
        "text/html",
        StringIO.StringIO(html).len,
        None
        )
    )
    # Save the raw file
    screenshot.html_raw.save("raw.html", InMemoryUploadedFile(
        StringIO.StringIO(html),
        None,
        "raw.html",
        "text/html",
        StringIO.StringIO(html).len,
        None
        )
    )
    # Check it off
    screenshot.has_html = True
    screenshot.save()

