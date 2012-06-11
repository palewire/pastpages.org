from django.db import models
from django.utils import timezone
from django.db.models import Count


class SiteManager(models.Manager):
    
    def active(self):
        return self.filter(status='active')


class UpdateManager(models.Manager):
    
    def dates(self):
        """
        Returns all the distinct dates that appear in the model.
        """
        return self.uniqify([timezone.localtime(i.start).date()
            for i in self.all()])
    
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
    
    def uniqify(self, seq, idfun=None): 
       # order preserving
       if idfun is None:
           def idfun(x): return x
       seen = {}
       result = []
       for item in seq:
           marker = idfun(item)
           # in old Python versions:
           # if seen.has_key(marker)
           # but in new ones:
           if marker in seen: continue
           seen[marker] = 1
           result.append(item)
       return result



