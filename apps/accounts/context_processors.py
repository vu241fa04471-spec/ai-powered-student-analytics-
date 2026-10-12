from apps.accounts.models import Role

def auth_roles(request):
    """
    Template context processor providing current user's role indicators.
    """
    user = request.user
    if not user.is_authenticated:
        return {
            'is_admin': False,
            'is_faculty': False,
            'is_placement_officer': False,
            'is_student': False,
            'current_user_role': None,
            'ROLES': Role,
        }

    return {
        'is_admin': user.is_superuser or user.role == Role.ADMIN,
        'is_faculty': user.role == Role.FACULTY,
        'is_placement_officer': user.role == Role.PLACEMENT_OFFICER,
        'is_student': user.role == Role.STUDENT,
        'current_user_role': user.role,
        'current_user_role_display': user.get_role_display(),
        'ROLES': Role,
    }
