from django.db import models

# Create your models here.
from Blender.models import Blenderrr
from Provider.models import TypeSet, PrivacyPolicyBase




class Request(models.Model):
    key = models.CharField(max_length=1000)
    certificate = models.URLField()
    blender = models.ForeignKey(Blenderrr)
    output = models.ForeignKey(TypeSet)

    def __unicode__(self):
        return "request #%d" % self.id

class Message(models.Model):
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"

    TYPE_CHOICES = (
        (ERROR, "Error"),
        (WARNING, "Warning"),
        (INFO, "Info"),
    )

    type = models.CharField(max_length=10,choices=TYPE_CHOICES,default=INFO)
    msg = models.CharField(max_length=1000)
    request = models.ForeignKey(Request)

    def __unicode__(self):
        return "%s: %s" % (self.type, self.msg)

class Assignment(models.Model):
    variable = models.CharField(max_length=100)
    value = models.CharField(max_length=1000)
    request = models.ForeignKey(Request)

    def __unicode__(self):
        return "%s: %s" % (self.variable, self.value)

class UserPrivacyPrefRule(PrivacyPolicyBase):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    SENSITIVITY_CHOICES = (
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    )
    sensitivity = models.SmallIntegerField(choices=SENSITIVITY_CHOICES,default=LOW)
    request = models.ForeignKey(Request)

    def __unicode__(self):
        return "UserPrivacyPreference %d" % self.id

class UserPrivacyPolicyRule(PrivacyPolicyBase):
    request = models.ForeignKey(Request)

    def __unicode__(self):
        return "UserPrivacyPolicy %d" % self.id



