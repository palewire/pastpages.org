"""
A postgres database backup script lifted from Samuel Clay's Newsblur
https://github.com/samuelclay/NewsBlur
"""
import os
import sys

CURRENT_DIR  = os.path.dirname(__file__)
PROJECT_DIR = ''.join([CURRENT_DIR, '/../../project/'])
sys.path.insert(0, PROJECT_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import time
import cloudfiles
from django.conf import settings

db_user = settings.DATABASES['default']['USER']
db_name = settings.DATABASES['default']['NAME']
db_pass = settings.DATABASES['default']['PASSWORD']
os.environ['PGPASSWORD'] = db_pass
filename = 'postgres_%s_%s.sql.gz' % (
    db_name,
    time.strftime('%Y-%m-%d-%H-%M')
)
cmd = 'pg_dump -U %s -Fc %s > %s' % (db_user, db_name, filename)

print 'Backing up PostgreSQL: %s' % cmd
os.system(cmd)

print 'Uploading %s to database backup...' % filename
conn = cloudfiles.get_connection(
    settings.CUMULUS['USERNAME'],
    settings.CUMULUS['API_KEY']
)
bucket = conn.get_container("pastpages.backups")
obj = bucket.create_object(filename)
obj.load_from_filename(filename)
os.remove(filename)
