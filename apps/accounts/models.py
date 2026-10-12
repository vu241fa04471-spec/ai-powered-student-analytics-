from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Role(models.TextChoices):
    ADMIN = 'ADMIN', _('Administrator')
    FACULTY = 'FACULTY', _('Faculty')
    PLACEMENT_OFFICER = 'PLACEMENT_OFFICER', _('Placement Officer')
    STUDENT = 'STUDENT', _('Student')

class User(AbstractUser):
    """
    Custom user model supporting role-based access for Smart Campus Analytics.
    """
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
        help_text=_("Primary institutional role determining system permissions")
    )
    phone_number = models.CharField(max_length=20, blank=True)
    employee_or_student_id = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Institutional Employee ID or Student Registration Number")
    )
    department = models.ForeignKey(
        'students.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='department_users',
        help_text=_("Department affiliation for faculty or staff")
    )
    designation = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("e.g. Assistant Professor, Dean, Placement Director")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['username']
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        full = self.get_full_name()
        name = full if full else self.username
        return f"{name} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == Role.ADMIN or self.is_superuser

    @property
    def is_faculty_role(self):
        return self.role == Role.FACULTY

    @property
    def is_placement_officer_role(self):
        return self.role == Role.PLACEMENT_OFFICER

    @property
    def is_student_role(self):
        return self.role == Role.STUDENT

    @property
    def role_badge_class(self):
        badges = {
            Role.ADMIN: 'bg-danger',
            Role.FACULTY: 'bg-primary',
            Role.PLACEMENT_OFFICER: 'bg-info text-dark',
            Role.STUDENT: 'bg-success',
        }
        return badges.get(self.role, 'bg-secondary')
