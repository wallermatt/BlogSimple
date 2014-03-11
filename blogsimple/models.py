from django.db import models

class Blog(models.Model):
    title  = models.CharField(max_length = 100)
    body   = models.TextField()
    posted = models.DateTimeField(db_index = True, auto_now_add = True)
    edited = models.DateTimeField(db_index = True, auto_now_add = True)

    def __unicode__(self):
        return str(self.title)
