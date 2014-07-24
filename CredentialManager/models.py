from django.db import models

# Create your models here.
from Provider.models import Expression


class User(models.Model):
    key = models.CharField(max_length=1000, unique=True)
    attributes = models.ManyToManyField(Expression)
