from django.db import models

class BuildNode(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    
    # ssh connection details
    host = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    ssh_key = models.TextField()
    