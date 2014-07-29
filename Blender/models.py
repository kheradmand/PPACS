from django.db import models

# Create your models here.
from Provider.models import Purpose, Service
from Repository.models import Repository


class Blenderrr(models.Model):
    name = models.CharField(max_length=100, unique=True)
    repos = models.ManyToManyField(Repository)
    pref = models.BooleanField(choices=Purpose.ONLY_FOR_CHOICES,default=Purpose.ONLY_FOR)
    wh = models.PositiveSmallIntegerField()
    wm = models.PositiveSmallIntegerField()
    wl = models.PositiveSmallIntegerField()
    def __unicode__(self):
        return self.name


