from django.db import models
from django.utils import timezone
from django.db.models import Count


class SiteManager(models.Manager):
    
    def active(self):
        return self.filter(status='active')
    
    def stats(self):
        from django.db import connection
        from archive.models import Site
        cursor = connection.cursor()
        sql = """
            SELECT
                site.id,
                site.name,
                site.slug,
                COUNT(ssht.id),
                MIN(ssht.timestamp),
                MAX(ssht.timestamp)
            FROM archive_site as site
            INNER JOIN archive_screenshot as ssht 
            ON site.id = ssht.site_id
            WHERE site.status = 'active'
            GROUP BY 1, 2, 3
            ORDER BY site.sortable_name
        """
        cursor.execute(sql)
        results = []
        for l in cursor.fetchall():
            results.append({
                'id': l[0],
                'name': l[1],
                'slug': l[2],
                'total_screenshots': l[3],
                'first_screenshot': l[4],
                'last_screenshot': l[5],
            })
        return results


class UpdateManager(models.Manager):
    
    def live(self):
        from django.db import connection
        from archive.models import Site
        cursor = connection.cursor()
        sites = Site.objects.active().count()
        cutoff = int(sites * 0.7)
        sql = """
            SELECT u.id, u.start, count(s.id)
            FROM (
             SELECT id, start
             FROM archive_update
             ORDER BY start DESC
             LIMIT 10
            ) as u
            INNER JOIN archive_screenshot as s
            ON u.id = s.update_id
            GROUP BY u.id, u.start
            HAVING count(s.id) > %(cutoff)s
            ORDER BY 2 DESC;
        """ % dict(cutoff=cutoff)
        cursor.execute(sql)
        results = [(row[0], row[2]) for row in cursor.fetchall()]
        if not results:
            return None
        latest_id = results[0][0]
        obj = self.model.objects.get(id=latest_id)
        latest_count = results[0][1]
        if latest_count < sites:
            obj.in_progress = True
        return obj
