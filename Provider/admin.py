from django.contrib import admin
from Provider.models import *

admin.site.register(Provider)
admin.site.register(Expression)
admin.site.register(DataType)
admin.site.register(Service)
admin.site.register(Input)
admin.site.register(Goal)
admin.site.register(Purpose)
admin.site.register(ServicePrivacyPolicyRule)
admin.site.register(UserPrivacyPolicyRule)
admin.site.register(AccessControlElement)
