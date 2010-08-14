from django.db import models
from django.db.models import Q

class Project(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    repository = models.CharField(max_length=255)
    ssh_key = models.TextField(blank=True)

    config_file = models.CharField(max_length=255,
        default="journey.conf/config")

    def __unicode__(self):
        return self.name

    @property
    def last_build(self):
        try:
            return self.build_set.all().order_by('-started')[0]
        except (self.build_set.model.DoesNotExist, IndexError):
            return None

    @property
    def last_stable_build(self):
        try:
            return self.build_set.filter(state='stable').order_by('-started')[0]
        except (self.build_set.model.DoesNotExist, IndexError):
            return None

    @property
    def outstanding_builds(self):
        return self.build_set.filter(Q(Q(state='queued') | Q(state='unknown')))

    @property
    def builds(self):
        return self.build_set.exclude(Q(Q(state='queued') | Q(state='unknown')))