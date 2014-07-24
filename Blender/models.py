from django.db import models

# Create your models here.
from Repository.models import Repository


class Blenderrr(models.Model):
    name = models.CharField(max_length=100, unique=True)
    repos = models.ManyToManyField(Repository)
    wh = models.PositiveSmallIntegerField()
    wm = models.PositiveSmallIntegerField()
    wl = models.PositiveSmallIntegerField()
    def __unicode__(self):
        return self.name


