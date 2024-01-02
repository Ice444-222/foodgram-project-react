from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, AuthenticationFailed


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_or_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS and not request.user.is_staff:
            raise MethodNotAllowed(request.method)
        return True
    
class SafeMethodOrAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS and not request.user.is_authenticated:
            raise AuthenticationFailed(request.method)
        return True
    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            if obj.author == request.user:
                return True
            raise PermissionDenied(request.method)
        return True
        



class IsAuthorOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (
                obj.author == request.user
                or request.user.is_admin_or_staff_or_mod
            )
        return False
