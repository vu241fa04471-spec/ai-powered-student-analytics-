from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Department(models.Model):
    """
    Academic Department (e.g., Computer Science, Electrical Engineering).
    """
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    established_year = models.PositiveIntegerField(default=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')

    def __str__(self):
        return f"{self.code} - {self.name}"


class Program(models.Model):
    """
    Academic Program / Degree (e.g. B.Tech Computer Science & Engineering).
    """
    DEGREE_CHOICES = [
        ('UG', _('Undergraduate (B.Tech / B.E)')),
        ('PG', _('Postgraduate (M.Tech / M.E / MCA)')),
        ('PHD', _('Doctorate (Ph.D)')),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    degree_type = models.CharField(max_length=10, choices=DEGREE_CHOICES, default='UG')
    total_semesters = models.PositiveSmallIntegerField(default=8)
    credits_required = models.PositiveIntegerField(default=160)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['department', 'name']
        verbose_name = _('Program')
        verbose_name_plural = _('Programs')

    def __str__(self):
        return f"{self.name} ({self.code})"


class AcademicYear(models.Model):
    """
    Academic calendar year (e.g. 2025-2026).
    """
    name = models.CharField(max_length=20, unique=True, help_text="e.g. 2025-2026")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']
        verbose_name = _('Academic Year')
        verbose_name_plural = _('Academic Years')

    def __str__(self):
        return self.name


class Semester(models.Model):
    """
    Academic Semester representation (1 through 8).
    """
    TERM_CHOICES = [
        ('ODD', _('Odd Semester (Fall)')),
        ('EVEN', _('Even Semester (Spring)')),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Semester number (1-8)"
    )
    term = models.CharField(max_length=10, choices=TERM_CHOICES, default='ODD')
    is_current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['academic_year', 'number']
        unique_together = ('academic_year', 'number')
        verbose_name = _('Semester')
        verbose_name_plural = _('Semesters')

    def __str__(self):
        return f"Sem {self.number} ({self.academic_year.name} - {self.get_term_display()})"


class EnrollmentStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', _('Active Enrolled')
    AT_RISK = 'AT_RISK', _('Academic Risk')
    ON_LEAVE = 'ON_LEAVE', _('Leave of Absence')
    GRADUATED = 'GRADUATED', _('Graduated')
    WITHDRAWN = 'WITHDRAWN', _('Withdrawn / Dropped')


class StudentProfile(models.Model):
    """
    Core normalized Student entity.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text=_("Unique institutional roll/registration ID (e.g. 2022CSE042)")
    )
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='students')
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='students')
    current_semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name='enrolled_students')
    section = models.CharField(max_length=5, default='A')
    admission_year = models.PositiveIntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2035)])
    expected_graduation_year = models.PositiveIntegerField()
    enrollment_status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ACTIVE,
        db_index=True
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentored_students',
        help_text=_("Faculty advisor or academic mentor")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_id']
        verbose_name = _('Student Profile')
        verbose_name_plural = _('Student Profiles')
        indexes = [
            models.Index(fields=['department', 'current_semester']),
            models.Index(fields=['enrollment_status']),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email

    def get_latest_cgpa(self):
        latest = self.academic_records.order_by('-semester__number').first()
        return float(latest.cgpa) if latest else 0.0

    def get_overall_attendance_percentage(self):
        from apps.attendance.models import SubjectAttendanceSummary
        summaries = SubjectAttendanceSummary.objects.filter(student=self)
        total_conducted = sum(s.total_classes for s in summaries)
        total_attended = sum(s.classes_attended for s in summaries)
        if total_conducted == 0:
            return 100.0
        return round((total_attended / total_conducted) * 100, 2)

    def get_active_backlogs_count(self):
        from apps.academics.models import BacklogRecord
        return BacklogRecord.objects.filter(student=self, status='ACTIVE').count()


class FacultyAssignment(models.Model):
    """
    Mapping between faculty, subject, semester, and section.
    """
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_assignments'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='faculty_assignments'
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='faculty_assignments')
    section = models.CharField(max_length=10, default='A')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('faculty', 'subject', 'semester', 'section', 'academic_year')
        verbose_name = _('Faculty Assignment')
        verbose_name_plural = _('Faculty Assignments')

    def __str__(self):
        return f"{self.faculty.get_full_name()} -> {self.subject.code} ({self.semester}, Sec {self.section})"
