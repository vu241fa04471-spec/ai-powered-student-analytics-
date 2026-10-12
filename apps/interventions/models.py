from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class InterventionCategory(models.TextChoices):
    ACADEMIC_TUTORING = 'ACADEMIC_TUTORING', _('Remedial Academic Tutoring')
    ATTENDANCE_COUNSELING = 'ATTENDANCE_COUNSELING', _('Attendance Counseling & Warning')
    CODING_BOOTCAMP = 'CODING_BOOTCAMP', _('Specialized Coding Bootcamp')
    MOCK_INTERVIEW_PREP = 'MOCK_INTERVIEW_PREP', _('Mock Interview Coaching')
    MENTOR_MEETING = 'MENTOR_MEETING', _('One-on-One Faculty Mentorship Session')
    COUNSELING_SUPPORT = 'COUNSELING_SUPPORT', _('Psychological / Wellbeing Counseling')


class InterventionPriority(models.TextChoices):
    LOW = 'LOW', _('Low Priority')
    MEDIUM = 'MEDIUM', _('Medium Priority')
    HIGH = 'HIGH', _('High Priority')
    URGENT = 'URGENT', _('Urgent Action Required')


class RecommendationStatus(models.TextChoices):
    PROPOSED = 'PROPOSED', _('Proposed by AI / System')
    APPROVED = 'APPROVED', _('Approved by Faculty')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    COMPLETED = 'COMPLETED', _('Completed')
    DISMISSED = 'DISMISSED', _('Dismissed / Overridden')


class InterventionRecommendation(models.Model):
    """
    AI or rule-generated intervention suggestion awaiting mentor/faculty action.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='intervention_recommendations'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=30,
        choices=InterventionCategory.choices,
        default=InterventionCategory.MENTOR_MEETING
    )
    priority = models.CharField(
        max_length=15,
        choices=InterventionPriority.choices,
        default=InterventionPriority.MEDIUM
    )
    generated_by_ai = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=RecommendationStatus.choices,
        default=RecommendationStatus.PROPOSED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = _('Intervention Recommendation')
        verbose_name_plural = _('Intervention Recommendations')

    def __str__(self):
        return f"[{self.priority}] {self.student.student_id}: {self.title}"


class InterventionStatus(models.TextChoices):
    PLANNED = 'PLANNED', _('Planned')
    ACTIVE = 'ACTIVE', _('Active / Ongoing')
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELLED = 'CANCELLED', _('Cancelled')


class InterventionRecord(models.Model):
    """
    Formal intervention workflow tracked by faculty or counselors.
    """
    recommendation = models.ForeignKey(
        InterventionRecommendation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='records'
    )
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='intervention_records'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_interventions'
    )
    intervention_type = models.CharField(max_length=100)
    action_plan = models.TextField()
    start_date = models.DateField()
    target_completion_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=InterventionStatus.choices,
        default=InterventionStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = _('Intervention Record')
        verbose_name_plural = _('Intervention Records')

    def __str__(self):
        return f"Intervention for {self.student.student_id} ({self.status}) - Assigned to {self.assigned_to.get_full_name()}"


class ImpactAssessment(models.TextChoices):
    POSITIVE = 'POSITIVE', _('Positive Progress')
    NO_CHANGE = 'NO_CHANGE', _('No Discernible Change')
    NEGATIVE = 'NEGATIVE', _('Negative / Worsened')


class InterventionFollowUp(models.Model):
    """
    Periodic progress notes during an active intervention.
    """
    intervention = models.ForeignKey(
        InterventionRecord,
        on_delete=models.CASCADE,
        related_name='follow_ups'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    follow_up_date = models.DateField()
    notes = models.TextField()
    student_response = models.TextField(blank=True)
    impact_assessment = models.CharField(
        max_length=20,
        choices=ImpactAssessment.choices,
        default=ImpactAssessment.POSITIVE
    )

    class Meta:
        ordering = ['-follow_up_date']
        verbose_name = _('Intervention Follow-Up')
        verbose_name_plural = _('Intervention Follow-Ups')

    def __str__(self):
        return f"Follow-up for {self.intervention.student.student_id} on {self.follow_up_date}"


class OutcomeStatus(models.TextChoices):
    SUCCESSFUL = 'SUCCESSFUL', _('Goal Achieved / Risk Mitigated')
    PARTIALLY_SUCCESSFUL = 'PARTIALLY_SUCCESSFUL', _('Partially Successful')
    UNSUCCESSFUL = 'UNSUCCESSFUL', _('Unsuccessful / Escalated to Committee')


class InterventionOutcome(models.Model):
    """
    Post-intervention result evaluation measuring KPI delta.
    """
    intervention = models.OneToOneField(
        InterventionRecord,
        on_delete=models.CASCADE,
        related_name='outcome'
    )
    outcome_status = models.CharField(
        max_length=25,
        choices=OutcomeStatus.choices,
        default=OutcomeStatus.SUCCESSFUL
    )
    pre_metric_value = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text=_("Starting metric e.g. Attendance 54% or CGPA 5.8")
    )
    post_metric_value = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text=_("Ending metric e.g. Attendance 78% or CGPA 6.9")
    )
    outcome_summary = models.TextField()
    closed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Intervention Outcome')
        verbose_name_plural = _('Intervention Outcomes')

    def __str__(self):
        return f"Outcome for {self.intervention.student.student_id}: {self.get_outcome_status_display()}"
