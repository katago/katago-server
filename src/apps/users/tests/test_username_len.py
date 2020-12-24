import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import DataError
from django.db import transaction

pytestmark = pytest.mark.django_db

User = get_user_model()

class TestUsernameLen:

    def setup_method(self):
        self.users = []
        self.bad_users = []

    def teardown_method(self):
        for user in self.users:
            user.delete()
        for user in self.bad_users:
            user.delete()

    def test_username_len(self):
        self.users.append(User.objects.create_user(username="123456789012345678901234567890123456789012345678901234567890", password="test"))
        with transaction.atomic():
            with pytest.raises(DataError):
                self.users.append(User.objects.create_user(username="1234567890123456789012345678901234567890123456789012345678901", password="test"))

        self.users.append(User.objects.create_user(username="123", password="test"))
        self.users.append(User.objects.create_user(username="quertyexample.com", password="test"))
        self.users.append(User.objects.create_user(username="thé", password="test"))
        self.users.append(User.objects.create_user(username="Jane_Doe", password="test"))
        self.users.append(User.objects.create_user(username="πβμ", password="test"))
        for user in self.users:
            user.full_clean()

        self.bad_users.append(User.objects.create_user(username="12", password="test"))
        self.bad_users.append(User.objects.create_user(username="b aa", password="test"))
        self.bad_users.append(User.objects.create_user(username="querty@example.com", password="test"))
        self.bad_users.append(User.objects.create_user(username="a", password="test"))
        self.bad_users.append(User.objects.create_user(username="ké", password="test"))
        self.bad_users.append(User.objects.create_user(username="Jane|Doe", password="test"))
        self.bad_users.append(User.objects.create_user(username="bob\n", password="test"))
        self.bad_users.append(User.objects.create_user(username="bob\t", password="test"))
        self.bad_users.append(User.objects.create_user(username="bob\b", password="test"))
        self.bad_users.append(User.objects.create_user(username="bob\r", password="test"))
        self.bad_users.append(User.objects.create_user(username="☺☺☺", password="test"))
        for user in self.bad_users:
            with pytest.raises(ValidationError):
                user.full_clean()

        with pytest.raises(ValueError):
            self.bad_users.append(User.objects.create_user(username="", password="test"))
        with transaction.atomic():
            with pytest.raises(ValueError):
                self.bad_users.append(User.objects.create_user(username="bob\x00", password="test"))


