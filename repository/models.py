import re

from django.db import models
from path import path


class Version(models.Model):
    major = models.IntegerField()
    minor = models.IntegerField()
    micro = models.IntegerField()

    def url(self):
        raise NotImplementedError

    def path(self):
        raise NotImplementedError

    class Meta:
        abstract = True
        ordering = ['major', 'minor', 'micro']


class Package(models.Model):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['name']
