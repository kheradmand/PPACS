from django.db import models

# Create your models here.
class Provider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    #service list

    def __unicode__(self):
        return self.name


class Expression(models.Model):
    EQUAL = '='
    NOT_EQUAL = '!='
    GREATER = '>'
    LESS = '<'
    GREATER_EQUAL = '>='
    LESS_EQUAL = '<='
    MEMBER = 'member of'
    SUBSET = 'strict subset of'
    SUPERSET = 'strict superset of'
    SUBSET_EQUAL = 'subset of'
    SUPERSET_EQUAL = 'superset of'
    OPERATOR_CHOICES = (
        (EQUAL, EQUAL),
        (NOT_EQUAL, NOT_EQUAL),
        (GREATER, GREATER),
        (GREATER_EQUAL, GREATER_EQUAL),
        (LESS, LESS),
        (LESS_EQUAL, LESS_EQUAL),
        (MEMBER, MEMBER),
        (SUBSET, SUBSET),
        (SUBSET_EQUAL, SUBSET_EQUAL),
        (SUPERSET, SUPERSET_EQUAL),
    )
    variable = models.CharField(max_length=100)
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, default=EQUAL)
    value = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s %s %s" % (self.variable, self.operator, self.value)

class DataType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

class Goal(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

#class TypeList(models.Model):
#    list = models.CharField(max_length=10000)
#    def __unicode__(self):
#        return self.list

class TypeSet(models.Model):
    types = models.ManyToManyField(DataType)

    def __unicode__(self):
        return '{%s}' % ', '.join(map(str, list(self.types.all())))


class Service(models.Model):
    name = models.CharField(max_length=100)
    provider = models.ForeignKey(Provider)
    inputs = models.ManyToManyField(TypeSet, related_name="service_input_set")
    output = models.ForeignKey(TypeSet, related_name="service_output_set")
    function = models.URLField(blank=True)
    #input
    #privacypolicyrule
    #accesscontrollist

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'provider')



class Purpose(models.Model):
    ONLY_FOR_CHOICES = (
        (True, "Only for"),
        (False, "Not For")
    )
    goal = models.ForeignKey(Goal)
    onlyFor = models.BooleanField(choices=ONLY_FOR_CHOICES,default=True)

    def __unicode__(self):
        return "%s for %s" % ("Only" if self.onlyFor == True else "Not", self.goal)


class PrivacyPolicyBase(models.Model):
    dataType = models.ForeignKey(DataType)
    purpose = models.ManyToManyField(Purpose)
    class Meta:
        abstract = True


class ServicePrivacyPolicyRule(PrivacyPolicyBase):
    service = models.ForeignKey(Service, related_name='service_privacy_policy_rule_set')
    ttl = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return "ServicePrivacyPolicy %d" % self.id



class AccessControlElement(models.Model):
    userRules = models.ManyToManyField(Expression, related_name="user+")
    environmentRules = models.ManyToManyField(Expression, related_name="env+")
    service = models.ForeignKey(Service, related_name="access_control_element_set")

    def __unicode__(self):
        return "AccessControlElement %d" % self.id










