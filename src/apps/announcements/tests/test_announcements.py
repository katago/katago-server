import pytest
import base64

from django.test import Client
from src.apps.announcements.models import Announcement

pytestmark = pytest.mark.django_db

class TestAnnouncements:

    def setup_method(self):
        self.announcements = []

    def teardown_method(self):
        for announcement in self.announcements:
            announcement.delete()

    def test_announcements(self):
        client = Client()
        response = client.get('/')
        assert(response.status_code == 200)
        content = response.content.decode("utf-8")
        assert("Test Announcement Title" not in content)
        assert("Here are some test contents" not in content)
        assert("Test Announcement Title Disabled" not in content)
        assert("This message should not show up" not in content)
        self.announcements.append(Announcement.objects.create(
            title="Test Announcement Title",
            contents = "Here are some test contents! And an <div>attempted div</div> and [link](https://example.com) :)",
            display_order = 10,
            enabled = True,
            notes = "",
        ))
        self.announcements.append(Announcement.objects.create(
            title="Test Announcement Title Disabled",
            contents = "This message should not show up",
            display_order = 20,
            enabled = False,
            notes = "",
        ))
        response = client.get('/')
        assert(response.status_code == 200)
        content = response.content.decode("utf-8")
        assert("Test Announcement Title" in content)
        assert("Here are some test contents" in content)
        assert("<div>attempted div</div>" not in content)
        assert("&lt;div&gt;attempted div&lt;/div&gt;" in content)
        assert('<a href="https://example.com">link</a>' in content)
        assert("Test Announcement Title Disabled" not in content)
        assert("This message should not show up" not in content)
