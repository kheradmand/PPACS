from django.db import models
from Provider.models import Service,TypeSet

# Create your models here.
class Repository(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


class Record(models.Model):
    service = models.ForeignKey(Service)
    repository = models.ForeignKey(Repository)
    reputation = models.PositiveSmallIntegerField()
    #mandatory_input = models.ForeignKey(TypeSet, related_name='mandatory_input_record_set')
    optional_input = models.ForeignKey(TypeSet, related_name='optional_input_record_set')
    output = models.ForeignKey(TypeSet, related_name='output_record_set')

    def __unicode__(self):
        return str(self.service)+" in "+str(self.repository)




