from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class AttendanceSession(models.Model):
    """
    Individual lecture/lab session conducted by faculty.
    """
    SESSION_TYPES = [
        ('LECTURE', _('Lecture')),
        ('LAB', _('Practical Lab')),
        ('TUTORIAL', _('Tutorial')),
    ]

    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conducted_sessions'
    )
    semester = models.ForeignKey(
        'students.Semester',
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )
    section = models.CharField(max_length=5, default='A')
    session_date = models.DateField()
    session_type = models.CharField(max_length=15, choices=SESSION_TYPES, default='LECTURE')
    topic_covered = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date', 'subject']
        verbose_name = _('Attendance Session')
        verbose_name_plural = _('Attendance Sessions')

    def __str__(self):
        return f"{self.subject.code} - {self.session_date} ({self.get_session_type_display()}, Sec {self.section})"


class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', _('Present')
    ABSENT = 'ABSENT', _('Absent')
    LATE = 'LATE', _('Late')
    EXCUSED = 'EXCUSED', _('Excused')


class AttendanceRecord(models.Model):
    """
    Student attendance for a specific session.
    """
    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records'
    )
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    status = models.CharField(
        max_length=10,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT
    )
    remarks = models.CharField(max_length=150, blank=True)

    class Meta:
        unique_together = ('session', 'student')
        ordering = ['session', 'student']
        verbose_name = _('Attendance Record')
        verbose_name_plural = _('Attendance Records')

    def __str__(self):
        return f"{self.student.student_id} - {self.session.subject.code} ({self.status})"


class SubjectAttendanceSummary(models.Model):
    """
    Aggregated subject-level attendance metric for fast reporting and analytics.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='student_attendance_summaries'
    )
    semester = models.ForeignKey(
        'students.Semester',
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    total_classes = models.PositiveIntegerField(default=0)
    classes_attended = models.PositiveIntegerField(default=0)
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    is_shortage = models.BooleanField(
        default=False,
        help_text=_("Flagged when attendance drops below the statutory 75% threshold")
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject', 'semester')
        ordering = ['student', 'subject']
        verbose_name = _('Subject Attendance Summary')
        verbose_name_plural = _('Subject Attendance Summaries')

    def clean(self):
        if self.classes_attended > self.total_classes:
            raise ValidationError({
                'classes_attended': _("Classes attended cannot exceed total conducted classes.")
            })

    def save(self, *args, **kwargs):
        self.clean()
        if self.total_classes > 0:
            self.attendance_percentage = round((self.classes_attended / self.total_classes) * 100, 2)
        else:
            self.attendance_percentage = 100.00
        self.is_shortage = self.attendance_percentage < 75.00
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code}: {self.classes_attended}/{self.total_classes} ({self.attendance_percentage}%)"
