from django.contrib import admin

from src.apps.runs.admin.run_admin import RunAdmin
from src.apps.runs.models import Run

admin.site.register(Run, RunAdmin)
