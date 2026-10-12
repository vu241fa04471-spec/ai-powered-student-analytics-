from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class FeedbackCategory(models.Model):
    """
    Taxonomy for student and institutional surveys.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Feedback Category')
        verbose_name_plural = _('Feedback Categories')

    def __str__(self):
        return self.name


class StudentFeedback(models.Model):
    """
    Course, faculty, or institutional feedback submitted by students.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks_given',
        help_text=_("Nullified if anonymous")
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_feedbacks'
    )
    semester = models.ForeignKey(
        'students.Semester',
        on_delete=models.CASCADE,
        related_name='student_feedbacks'
    )
    category = models.ForeignKey(
        FeedbackCategory,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    satisfaction_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("1 (Poor) to 5 (Excellent)")
    )
    comments = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Student Feedback')
        verbose_name_plural = _('Student Feedbacks')

    def __str__(self):
        source = "Anonymous" if self.is_anonymous or not self.student else self.student.student_id
        return f"{source} -> {self.category.name} ({self.satisfaction_score}/5)"


class FacultyFeedback(models.Model):
    """
    Qualitative assessments provided by faculty mentors about a student.
    """
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_evaluations'
    )
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='faculty_feedbacks'
    )
    semester = models.ForeignKey(
        'students.Semester',
        on_delete=models.CASCADE,
        related_name='faculty_evaluations'
    )
    academic_aptitude_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("1 (Low) to 5 (Outstanding)")
    )
    discipline_attendance_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    improvement_notes = models.TextField(blank=True)
    confidential_remarks = models.TextField(
        blank=True,
        help_text=_("Strictly restricted to academic mentors and administrators")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Faculty Evaluation')
        verbose_name_plural = _('Faculty Evaluations')

    def __str__(self):
        return f"Faculty {self.faculty.get_full_name()} evaluation for {self.student.student_id}"
