from django.contrib import admin
from django.contrib.auth import get_user_model

from .user_admin import UserAdmin

User = get_user_model()
admin.site.register(User, UserAdmin)

from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django_celery_beat.models import SolarSchedule, CrontabSchedule, ClockedSchedule

admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
