from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Subject(models.Model):
    """
    Course/Subject definition.
    """
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    department = models.ForeignKey(
        'students.Department',
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    semester_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    credits = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=3.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(10.0)]
    )
    is_elective = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['department', 'semester_number', 'code']
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')

    def __str__(self):
        return f"{self.code} - {self.name} (Sem {self.semester_number})"


class AcademicRecord(models.Model):
    """
    Consolidated semester result and CGPA tracking.
    """
    STATUS_CHOICES = [
        ('PASS', _('Pass')),
        ('FAIL', _('Fail / Backlogs')),
        ('PROBATION', _('Academic Probation')),
    ]

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='academic_records'
    )
    semester = models.ForeignKey(
        'students.Semester',
        on_delete=models.CASCADE,
        related_name='academic_records'
    )
    sgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text=_("Semester Grade Point Average (0.00 - 10.00)")
    )
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text=_("Cumulative Grade Point Average (0.00 - 10.00)")
    )
    credits_registered = models.DecimalField(max_digits=4, decimal_places=1, default=24.0)
    credits_earned = models.DecimalField(max_digits=4, decimal_places=1, default=24.0)
    backlogs_in_semester = models.PositiveIntegerField(default=0)
    cumulative_backlogs = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PASS')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['student', 'semester__number']
        unique_together = ('student', 'semester')
        verbose_name = _('Academic Record')
        verbose_name_plural = _('Academic Records')

    def __str__(self):
        return f"{self.student.student_id} - {self.semester} (SGPA: {self.sgpa}, CGPA: {self.cgpa})"


class AssessmentType(models.TextChoices):
    MID_TERM_1 = 'MID_TERM_1', _('Mid-Term Examination 1')
    MID_TERM_2 = 'MID_TERM_2', _('Mid-Term Examination 2')
    INTERNAL = 'INTERNAL', _('Continuous Internal Evaluation')
    END_SEM = 'END_SEM', _('End Semester Examination')
    ASSIGNMENT = 'ASSIGNMENT', _('Course Assignment / Project')


class AssessmentResult(models.Model):
    """
    Subject-level assessment scores.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='assessment_results'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='assessment_results'
    )
    semester = models.ForeignKey(
        'students.Semester',
        on_delete=models.CASCADE,
        related_name='assessment_results'
    )
    assessment_type = models.CharField(
        max_length=20,
        choices=AssessmentType.choices,
        default=AssessmentType.INTERNAL
    )
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    max_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.0,
        validators=[MinValueValidator(1.0)]
    )
    assessment_date = models.DateField()

    class Meta:
        ordering = ['-assessment_date', 'subject']
        verbose_name = _('Assessment Result')
        verbose_name_plural = _('Assessment Results')

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} ({self.get_assessment_type_display()}): {self.marks_obtained}/{self.max_marks}"

    @property
    def percentage(self):
        if self.max_marks > 0:
            return round((float(self.marks_obtained) / float(self.max_marks)) * 100, 2)
        return 0.0


class BacklogRecord(models.Model):
    """
    Tracking active and cleared backlogs.
    """
    STATUS_CHOICES = [
        ('ACTIVE', _('Active Backlog')),
        ('CLEARED', _('Cleared')),
    ]

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='backlogs'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='backlog_records'
    )
    semester_failed = models.ForeignKey(
        'students.Semester',
        on_delete=models.CASCADE,
        related_name='failed_backlogs'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    attempts_count = models.PositiveSmallIntegerField(default=1)
    cleared_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['student', 'status', 'subject']
        verbose_name = _('Backlog Record')
        verbose_name_plural = _('Backlog Records')

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} [{self.get_status_display()}]"
