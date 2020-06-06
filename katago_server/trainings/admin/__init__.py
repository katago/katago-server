from django.contrib import admin

from katago_server.trainings.admin.network_admin import NetworkAdmin
from katago_server.trainings.models import Network

admin.site.register(Network, NetworkAdmin)
