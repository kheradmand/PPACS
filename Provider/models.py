from django.db import models

# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    #service list


class Expression(models.Model):
    variable = models.CharField(max_length=100)
    operator = models.CharField(max_length=1)
    value = models.CharField(max_length=100)

class DataType(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Goal(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Service(models.Model):
    name = models.CharField(max_length=100)
    provider = models.ForeignKey(Provider)
    output = models.ForeignKey(DataType)
    function = models.URLField(blank=True)
    #input
    #privacypolicyrule
    #accesscontrollist


class Input(models.Model): #TODO: refine
    input = models.CharField(max_length=10000)
    service = models.ForeignKey(Service, related_name='input_set')


class Purpose(models.Model):
    goal = models.ForeignKey(Goal)
    onlyFor = models.BooleanField() #TODO: chage to choices


class PrivacyPolicyBase(models.Model):
    dataType = models.ForeignKey(DataType)
    purpose = models.ManyToManyField(Purpose)
    class Meta:
        abstract = True

class ServicePrivacyPolicyRule(PrivacyPolicyBase):
    service = models.ForeignKey(Service, related_name='service_privacy_policy_rule_set')
    ttl = models.PositiveSmallIntegerField()

class UserPrivacyPolicyRule(PrivacyPolicyBase):
    sensitivity = models.SmallIntegerField() #TODO: chage to choices

class AccessControlElement(models.Model):
    userRules = models.ManyToManyField(Expression, related_name="user+")
    environmentRules = models.ManyToManyField(Expression, related_name="env+")
    service = models.ForeignKey(Service, related_name="access_control_element_set")











