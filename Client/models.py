from django.db import models

# Create your models here.
from Blender.models import Blenderrr
from Provider.models import TypeSet, PrivacyPolicyBase, Service


class Request(models.Model):
    certificate = models.URLField()
    blender = models.ForeignKey(Blenderrr)
    output = models.ForeignKey(TypeSet)

    def get_sensitive_data(self, level):
        ret = set()
        for rule in self.userprivacyprefrule_set.filter(sensitivity=level):
            ret.add(rule.dataType.name)
        return ret

    def add_msg(self, type, msg):
        message = Message()
        message.type = type
        message.msg = msg
        message.request = self
        message.save()


    def __unicode__(self):
        return "request #%d" % self.id

class ChainElement(models.Model):
    index = models.PositiveSmallIntegerField()
    service = models.ForeignKey(Service)
    request = models.ForeignKey(Request)


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



