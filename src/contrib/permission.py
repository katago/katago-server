from allauth.account.models import EmailAddress
from django.conf import settings
from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ReadOrAuthCreateOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user and request.user.is_authenticated:
            if hasattr(settings, "DRF_ACCOUNT_EMAIL_VERIFICATION") and settings.DRF_ACCOUNT_EMAIL_VERIFICATION:
                return EmailAddress.objects.filter(user=request.user, verified=True).exists()
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class AuthOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if hasattr(settings, "DRF_ACCOUNT_EMAIL_VERIFICATION") and settings.DRF_ACCOUNT_EMAIL_VERIFICATION:
                return EmailAddress.objects.filter(user=request.user, verified=True).exists()
            return True
        return False
