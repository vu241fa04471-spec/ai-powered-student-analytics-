from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'designation', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'department')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'employee_or_student_id')
    ordering = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Smart Campus Profile', {
            'fields': ('role', 'employee_or_student_id', 'department', 'designation', 'phone_number', 'profile_picture'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Smart Campus Profile', {
            'fields': ('role', 'employee_or_student_id', 'department', 'designation', 'phone_number'),
        }),
    )
