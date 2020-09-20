from django.contrib import admin

from src.apps.trainings.admin.network_admin import NetworkAdmin
from src.apps.trainings.models import Network

admin.site.register(Network, NetworkAdmin)
