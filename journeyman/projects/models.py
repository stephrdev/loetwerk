from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    #Repository
    repository = models.CharField(max_length=255)
    ssh_key = models.TextField(blank=True)

    #Build
    config_file = models.CharField(max_length=255, default="journey.conf/config")

    def __unicode__(self):
        return self.name

    @property
    def last_build(self):
        try:
            return self.build_set.all().order_by('-started')[0]
        except:
            return None

    @property
    def last_successful_build(self):
        try:
            return self.build_set.filter(state='stable').order_by('-started')[0]
        except:
            return None
