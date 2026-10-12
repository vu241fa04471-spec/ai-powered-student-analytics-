from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import permissions

from apps.accounts.models import Role

def role_required(*allowed_roles):
    """
    Decorator for views that checks if the logged-in user possesses one of the allowed roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('accounts:login')}?next={request.path}")
            
            # Superusers always pass
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            raise PermissionDenied("You do not have the required role to access this resource.")
        return _wrapped_view
    return decorator


class RoleRequiredMixin(AccessMixin):
    """
    CBV mixin that verifies the user has one of the required roles.
    """
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser or request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("You do not have the required role to view this page.")


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (Role.ADMIN,)


class FacultyRequiredMixin(RoleRequiredMixin):
    allowed_roles = (Role.ADMIN, Role.FACULTY)


class PlacementOfficerRequiredMixin(RoleRequiredMixin):
    allowed_roles = (Role.ADMIN, Role.PLACEMENT_OFFICER)


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = (Role.STUDENT,)


# Helper functions for data-level authorization
def get_authorized_students_queryset(user):
    """
    Returns the queryset of StudentProfile objects that the user is permitted to see.
    - Admin: All students
    - Placement Officer: All students
    - Faculty: Students belonging to the faculty's department or taught by faculty
    - Student: Only their own StudentProfile
    """
    from apps.students.models import StudentProfile

    if not user.is_authenticated:
        return StudentProfile.objects.none()

    if user.is_superuser or user.role in (Role.ADMIN, Role.PLACEMENT_OFFICER):
        return StudentProfile.objects.all()

    if user.role == Role.FACULTY:
        # If faculty has a department, filter by department or subjects assigned
        qs = StudentProfile.objects.all()
        if user.department_id:
            return qs.filter(department_id=user.department_id)
        # Or mentored students
        return qs.filter(mentor=user)

    if user.role == Role.STUDENT:
        return StudentProfile.objects.filter(user=user)

    return StudentProfile.objects.none()


def can_user_access_student(user, student_profile):
    """
    Check if a specific user can view/manage a specific student profile.
    Critical server-side authorization check!
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser or user.role in (Role.ADMIN, Role.PLACEMENT_OFFICER):
        return True

    if user.role == Role.STUDENT:
        return student_profile.user_id == user.id

    if user.role == Role.FACULTY:
        if user.department_id and student_profile.department_id == user.department_id:
            return True
        if student_profile.mentor_id == user.id:
            return True
        # Check faculty subject assignments
        from apps.students.models import FacultyAssignment
        taught_student_count = FacultyAssignment.objects.filter(
            faculty=user,
            semester=student_profile.current_semester,
            subject__department=student_profile.department
        ).count()
        return taught_student_count > 0

    return False


# DRF Permissions
class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == Role.ADMIN)
        )


class IsFacultyOrAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.is_superuser or request.user.role in (Role.ADMIN, Role.FACULTY))
        )


class IsPlacementOfficerOrAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.is_superuser or request.user.role in (Role.ADMIN, Role.PLACEMENT_OFFICER))
        )


class CanAccessStudentDataDRF(permissions.BasePermission):
    """
    Object-level permission to ensure users can only access permitted student data.
    """
    def has_object_permission(self, request, view, obj):
        # Determine student profile from object
        student_profile = getattr(obj, 'student', None) or (obj if hasattr(obj, 'student_id') else None)
        if not student_profile:
            return True
        return can_user_access_student(request.user, student_profile)
