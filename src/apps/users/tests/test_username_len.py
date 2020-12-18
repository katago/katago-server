import pytest

from django.contrib.auth import get_user_model
from django.db.utils import DataError
from django.db import transaction

pytestmark = pytest.mark.django_db

User = get_user_model()

class TestUsernameLen:

    def setup_method(self):
        self.users = []

    def teardown_method(self):
        for user in self.users:
            user.delete()

    def test_username_len(self):
        self.users.append(User.objects.create_user(username="123456789012345678901234567890123456789012345678901234567890", password="test"))
        with transaction.atomic():
            with pytest.raises(DataError):
                self.users.append(User.objects.create_user(username="1234567890123456789012345678901234567890123456789012345678901", password="test"))
        for user in self.users:
            user.full_clean()
