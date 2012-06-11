import os
import cloudfiles
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = '<date YYYY-MM-DD>'
    help = 'Load a database snapshot from our nightly archive. Pulls latest by default. Specify date for an older one.'
    
    def handle(self, *args, **options): 
        # If the user provides a date, try to use that
        if args:
            try:
                dt = datetime.strptime(args[0], '%Y-%m-%d')
            except ValueError:
                raise CommandError("The date you submitted is not valid.")
        # Otherwise just use the today minus one day
        else:
            dt = datetime.now().date() - timedelta(days=1)
        
        # Download the snapshot
        filename = self.download(dt)
        
        # Load the snapshot into the database
        self.load("pastpages_%s" % dt.strftime("%Y-%m-%d"), filename)
    
    def load(self, target, source):
        """
        Load a database snapshot into our postgres installation.
        """
        # Set some vars
        os.environ['PGPASSWORD'] = settings.DATABASES['default']['PASSWORD']
        user = settings.DATABASES['default']['USER']
        print "Loading to new database %s" % target
        # If the db already exists, we need to drop it.
        try:
            os.system("sudo -u %s dropdb %s" % (user, target))
        except:
            pass
        # Create the database
        os.system("sudo -u %s createdb %s" % (user, target))
        # Load the data
        os.system("sudo -u %s pg_restore -Fc -d %s ./%s" % (user, target, source))
        # Delete the snapshot
        os.system("rm ./%s" % source)

    def download(self, dt):
        """
        Download a database snapshot.
        """
        # Craft up what the beginning of the snapshot should be
        prefix = 'postgres_pastpages_%s' % dt.strftime('%Y-%m-%d')
        
        # Log into our bucket
        conn = cloudfiles.get_connection(
            settings.CUMULUS['USERNAME'],
            settings.CUMULUS['API_KEY']
        )
        bucket = conn.get_container("pastpages.backups")
        
        # Loop through all of the objects and look for a match
        for obj in bucket.get_objects():
            if obj.name.startswith(prefix):
                print "Downloading %s" % obj.name
                # If you find it, download it
                obj.save_to_filename(obj.name)
                return obj.name
        raise CommandError("The date you provided could not be found in the archive.")


