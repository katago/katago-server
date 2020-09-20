from django.contrib import admin

from src.apps.startposes.admin.startpos_admin import StartPosAdmin
from src.apps.startposes.models import StartPos

admin.site.register(StartPos, StartPosAdmin)
