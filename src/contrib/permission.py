from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ReadOrCreateOnly(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS
