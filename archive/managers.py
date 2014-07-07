from django.db import models
from datetime import timedelta
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
                site.sortable_name,
                site.slug,
                SUM(CASE WHEN ssht.has_image = true THEN 1 ELSE 0 END),
                SUM(CASE WHEN ssht.has_html = true THEN 1 ELSE 0 END),
                MIN(ssht.timestamp),
                MAX(ssht.timestamp)
            FROM archive_site as site
            INNER JOIN archive_screenshot as ssht
            ON site.id = ssht.site_id
            WHERE site.status = 'active'
            GROUP BY 1, 2, 3, 4
        """
        cursor.execute(sql)
        results = []
        for l in cursor.fetchall():
            results.append({
                'id': l[0],
                'name': l[1],
                'sortable_name': l[2],
                'slug': l[3],
                'total_images': l[4],
                'total_html': l[5],
                'first_screenshot': timezone.localtime(l[6]),
                'last_screenshot': timezone.localtime(l[7]),
                'tardy': (timezone.now() - timezone.localtime(l[7])) > timedelta(days=1),
            })
        return sorted(results, key=lambda x: x['sortable_name'])


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
             LIMIT 25
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

    def stats(self, limit=50):
        from django.db import connection
        from archive.models import Site
        cursor = connection.cursor()
        sql = """
            SELECT
                update.id,
                update.start,
                COUNT(ssht.id)
            FROM archive_update as update
            INNER JOIN archive_screenshot as ssht 
            ON update.id = ssht.update_id
            GROUP BY 1, 2
            ORDER BY 2 DESC
            LIMIT %s
        """ % limit
        cursor.execute(sql)
        results = []
        for l in cursor.fetchall():
            results.append({
                'id': l[0],
                'start': timezone.localtime(l[1]),
                'screenshots': l[2],
            })
        return results[1:]
