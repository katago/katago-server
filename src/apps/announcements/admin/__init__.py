from django.contrib import admin

from src.apps.announcements.admin.announcement_admin import AnnouncementAdmin
from src.apps.announcements.models import Announcement

admin.site.register(Announcement, AnnouncementAdmin)
