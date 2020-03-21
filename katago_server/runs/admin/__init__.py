from django.contrib import admin

from katago_server.runs.admin.run_admin import RunAdmin
from katago_server.runs.models import Run

admin.site.register(Run, RunAdmin)

