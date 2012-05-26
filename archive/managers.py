from django.db import models


class SiteManager(models.Manager):
    pass


class UpdateManager(models.Manager):
    
    def live(self):
        from django.db import connection
        from archive.models import Site
        cursor = connection.cursor()
        sites = Site.objects.filter(status='active').count()
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




