from django.contrib import admin

# Register your models here.
from Repository.models import Repository, Record

admin.site.register(Repository)
admin.site.register(Record)