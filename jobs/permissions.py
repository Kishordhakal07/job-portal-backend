from rest_framework.permissions import BasePermission


class IsJobOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'company_profile') and
            obj.company == request.user.company_profile
        )