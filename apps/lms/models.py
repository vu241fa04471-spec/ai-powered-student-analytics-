from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class LMSActivityType(models.TextChoices):
    LOGIN = 'LOGIN', _('Platform Login')
    RESOURCE_VIEW = 'RESOURCE_VIEW', _('Learning Resource View')
    FORUM_POST = 'FORUM_POST', _('Discussion Forum Post')
    VIDEO_WATCH = 'VIDEO_WATCH', _('Video Lecture Watch')
    QUIZ_ACCESS = 'QUIZ_ACCESS', _('Quiz Attempt')


class LMSActivity(models.Model):
    """
    Granular LMS digital engagement actions.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='lms_activities'
    )
    activity_type = models.CharField(max_length=20, choices=LMSActivityType.choices)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=10)
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('LMS Activity')
        verbose_name_plural = _('LMS Activities')

    def __str__(self):
        return f"{self.student.student_id} - {self.get_activity_type_display()} at {self.timestamp}"


class SubmissionStatus(models.TextChoices):
    ON_TIME = 'ON_TIME', _('Submitted On-Time')
    LATE = 'LATE', _('Submitted Late')
    MISSED = 'MISSED', _('Missed / Unsubmitted')


class LMSAssignmentSubmission(models.Model):
    """
    Course assignment submissions and timeliness tracking.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='assignment_submissions'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='lms_assignments'
    )
    title = models.CharField(max_length=200)
    due_date = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=15,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.ON_TIME
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)

    class Meta:
        ordering = ['-due_date']
        verbose_name = _('LMS Assignment Submission')
        verbose_name_plural = _('LMS Assignment Submissions')

    def __str__(self):
        return f"{self.student.student_id} - {self.title} ({self.status})"


class LMSQuizAttempt(models.Model):
    """
    LMS module quiz attempts.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz_title = models.CharField(max_length=200)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    attempted_at = models.DateTimeField()

    class Meta:
        ordering = ['-attempted_at']
        verbose_name = _('LMS Quiz Attempt')
        verbose_name_plural = _('LMS Quiz Attempts')

    def __str__(self):
        return f"{self.student.student_id} - {self.quiz_title}: {self.score}/{self.total_score}"


class LMSEngagementSummary(models.Model):
    """
    Aggregated LMS engagement index per student per semester.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='lms_summaries'
    )
    semester = models.ForeignKey(
        'students.Semester',
        on_delete=models.CASCADE,
        related_name='lms_summaries'
    )
    total_logins = models.PositiveIntegerField(default=0)
    avg_weekly_logins = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    assignments_completed = models.PositiveIntegerField(default=0)
    assignments_late = models.PositiveIntegerField(default=0)
    assignments_missed = models.PositiveIntegerField(default=0)
    resources_accessed_count = models.PositiveIntegerField(default=0)
    lms_engagement_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=75.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Composite LMS Engagement Index (0 - 100)")
    )
    last_activity_date = models.DateTimeField(null=True, blank=True)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'semester')
        ordering = ['student', 'semester']
        verbose_name = _('LMS Engagement Summary')
        verbose_name_plural = _('LMS Engagement Summaries')

    def __str__(self):
        return f"{self.student.student_id} - LMS Score: {self.lms_engagement_score}/100"
