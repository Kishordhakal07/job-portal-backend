from rest_framework.permissions import BasePermission


class IsJobSeeker(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'job_seeker'
        )


class IsCompany(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'company'
        )