from django.db import models

class BuildNode(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    host = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    ssh_key = models.TextField()

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.host)
