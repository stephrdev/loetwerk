from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    #Repository
    repository = models.CharField(max_length=255)
    ssh_key = models.TextField(blank=True)

    #Build
    config_dir = models.CharField(max_length=255, default="journey.conf")

    def __unicode__(self):
        return self.name
