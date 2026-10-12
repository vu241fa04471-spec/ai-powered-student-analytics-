from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class ScoreTier(models.TextChoices):
    EXCELLENT = 'EXCELLENT', _('Excellent (>= 85)')
    GOOD = 'GOOD', _('Good (70 - 84)')
    AVERAGE = 'AVERAGE', _('Average (55 - 69)')
    AT_RISK = 'AT_RISK', _('At Risk (< 55)')
    INSUFFICIENT = 'INSUFFICIENT', _('Insufficient Data')


class ConfidenceLevel(models.TextChoices):
    HIGH = 'HIGH', _('High Confidence (>= 80% Completeness)')
    MEDIUM = 'MEDIUM', _('Medium Confidence (60 - 79% Completeness)')
    LOW = 'LOW', _('Low Confidence (40 - 59% Completeness)')
    INSUFFICIENT = 'INSUFFICIENT', _('Insufficient Data (< 40% Completeness)')


class PerformanceTrend(models.TextChoices):
    IMPROVING = 'IMPROVING', _('Improving')
    STABLE = 'STABLE', _('Stable')
    DECLINING = 'DECLINING', _('Declining')


class StudentSuccessSnapshot(models.Model):
    """
    Time-series snapshot of multidimensional student success score with explainable breakdown.
    Supports transparent, re-weighted missing data handling and confidence tracking.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='success_snapshots'
    )
    snapshot_date = models.DateField(auto_now_add=True, db_index=True)
    
    # 6-Dimension Component Scores (Normalized 0 - 100)
    academic_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Academic dimension (CGPA, SGPA trajectory, backlogs)")
    )
    attendance_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Attendance dimension across subjects")
    )
    engagement_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("LMS digital activity & timeliness")
    )
    extracurricular_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Clubs, hackathons, workshops, and verified certifications")
    )
    placement_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Career readiness, aptitude, coding tests, and mock interviews")
    )
    skills_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Verified technical & soft skills benchmark")
    )
    
    # Composite Score & Data Completeness
    composite_success_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Weighted composite AI success score (0 - 100)")
    )
    score_tier = models.CharField(
        max_length=20,
        choices=ScoreTier.choices,
        default=ScoreTier.GOOD
    )
    trend = models.CharField(
        max_length=15,
        choices=PerformanceTrend.choices,
        default=PerformanceTrend.STABLE
    )
    data_completeness = models.DecimalField(
        max_digits=5, decimal_places=2, default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Percentage of indicator dimensions with available evidence")
    )
    confidence_level = models.CharField(
        max_length=20,
        choices=ConfidenceLevel.choices,
        default=ConfidenceLevel.HIGH
    )
    is_insufficient_data = models.BooleanField(
        default=False,
        help_text=_("Flagged when evidence completeness is below reliable threshold (< 40%)")
    )
    available_indicators = models.JSONField(
        default=list,
        help_text=_("List of indicator keys with valid observations")
    )
    missing_indicators = models.JSONField(
        default=list,
        help_text=_("List of indicator keys missing observation data")
    )
    score_breakdown = models.JSONField(
        default=dict,
        help_text=_("Explainable AI feature weights, linear contributions, and drivers")
    )
    scoring_version = models.CharField(
        max_length=50, default='v2.0-transparent-weighted',
        help_text=_("Audit trail version for the scoring rules and weight configuration")
    )

    class Meta:
        ordering = ['-snapshot_date']
        verbose_name = _('Student Success Snapshot')
        verbose_name_plural = _('Student Success Snapshots')

    def __str__(self):
        return f"{self.student.student_id} Success: {self.composite_success_score}/100 [{self.score_tier}]"


class RiskLevel(models.TextChoices):
    LOW = 'LOW', _('Low Risk (Safe)')
    MEDIUM = 'MEDIUM', _('Moderate / Watchlist')
    HIGH = 'HIGH', _('High Academic Risk')
    CRITICAL = 'CRITICAL', _('Critical Immediate Intervention Needed')
    INSUFFICIENT = 'INSUFFICIENT', _('Insufficient Data')


class AcademicRiskAssessment(models.Model):
    """
    Predictive and rule-based assessment for academic failure/drop-out risk.
    Records observed indicators, thresholds, severity, and evidence completeness.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='academic_risk_assessments'
    )
    assessed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    risk_level = models.CharField(
        max_length=15,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        db_index=True
    )
    risk_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=15.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Composite rule-based risk severity score (0 - 100)")
    )
    risk_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_("Calibrated model probability of academic jeopardy (0.0 to 1.0)")
    )
    predicted_outcome = models.CharField(max_length=100, default='On-track for graduation')
    key_drivers = models.JSONField(
        default=list,
        help_text=_("Explainable risk factor drivers (e.g. low attendance, continuous grade drop)")
    )
    risk_factors = models.JSONField(
        default=list,
        help_text=_("Detailed audit of observed values vs statutory thresholds")
    )
    evidence_completeness = models.DecimalField(
        max_digits=5, decimal_places=2, default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    model_version = models.CharField(max_length=50, default='v2.0-explainable-rules')

    class Meta:
        ordering = ['-assessed_at']
        verbose_name = _('Academic Risk Assessment')
        verbose_name_plural = _('Academic Risk Assessments')

    def __str__(self):
        return f"{self.student.student_id} - Risk: {self.get_risk_level_display()} (Prob: {self.risk_probability:.2f})"

    @property
    def badge_class(self):
        badges = {
            RiskLevel.LOW: 'bg-success',
            RiskLevel.MEDIUM: 'bg-info text-dark',
            RiskLevel.HIGH: 'bg-warning text-dark',
            RiskLevel.CRITICAL: 'bg-danger',
            RiskLevel.INSUFFICIENT: 'bg-secondary',
        }
        return badges.get(self.risk_level, 'bg-secondary')


class PlacementReadinessStatus(models.TextChoices):
    TIER_1_READY = 'TIER_1_READY', _('Tier-1 Company Ready')
    READY = 'READY', _('General Drive Ready')
    BORDERLINE = 'BORDERLINE', _('Borderline (Needs Fast-Track Practice)')
    AT_RISK = 'AT_RISK', _('High Risk / Low Readiness')
    INSUFFICIENT = 'INSUFFICIENT', _('Insufficient Data')


class PlacementRiskAssessment(models.Model):
    """
    Assessment of placement preparation and skill competencies.
    Carefully distinguishes between readiness level and job offer probability.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='placement_risk_assessments'
    )
    assessed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    readiness_status = models.CharField(
        max_length=20,
        choices=PlacementReadinessStatus.choices,
        default=PlacementReadinessStatus.READY
    )
    readiness_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=65.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Placement competency score (0 - 100)")
    )
    evidence_completeness = models.DecimalField(
        max_digits=5, decimal_places=2, default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    skill_gaps = models.JSONField(
        default=list,
        help_text=_("Specific identified weaknesses (e.g. Dynamic Programming, Verbal English)")
    )
    suggested_activities = models.JSONField(
        default=list,
        help_text=_("Targeted career preparation recommendations")
    )
    recommended_focus = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-assessed_at']
        verbose_name = _('Placement Risk Assessment')
        verbose_name_plural = _('Placement Risk Assessments')

    def __str__(self):
        return f"{self.student.student_id} - Placement: {self.get_readiness_status_display()} ({self.readiness_score}%)"


class RiskIndicatorCategory(models.TextChoices):
    ACADEMIC = 'ACADEMIC', _('Academic Performance')
    ATTENDANCE = 'ATTENDANCE', _('Attendance Deficit')
    LMS = 'LMS', _('LMS Inactivity')
    PLACEMENT = 'PLACEMENT', _('Placement Skill Gap')
    BEHAVIORAL = 'BEHAVIORAL', _('Disciplinary / Behavioral')


class RiskSeverity(models.TextChoices):
    INFO = 'INFO', _('Informational')
    WARNING = 'WARNING', _('Early Warning')
    CRITICAL = 'CRITICAL', _('Critical Action Required')


class RiskIndicator(models.Model):
    """
    Discrete, auditable risk alerts generated by the system rules or AI models.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='risk_indicators'
    )
    category = models.CharField(
        max_length=20,
        choices=RiskIndicatorCategory.choices,
        default=RiskIndicatorCategory.ACADEMIC
    )
    title = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    severity = models.CharField(
        max_length=15,
        choices=RiskSeverity.choices,
        default=RiskSeverity.WARNING
    )
    is_resolved = models.BooleanField(default=False, db_index=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-detected_at']
        verbose_name = _('Risk Indicator')
        verbose_name_plural = _('Risk Indicators')

    def __str__(self):
        return f"[{self.severity}] {self.student.student_id}: {self.title}"


class StudentSegment(models.Model):
    """
    Behavioral cohorts (Segments A through F: High Flyers, Placement Gaps, Attendance Issues, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    criteria_summary = models.TextField(help_text=_("Analytical logic defining this cohort"))
    badge_color = models.CharField(max_length=25, default='#2563EB')
    students = models.ManyToManyField(
        'students.StudentProfile',
        related_name='segments',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Student Segment')
        verbose_name_plural = _('Student Segments')

    def __str__(self):
        return self.name


class ModelEvaluationResult(models.Model):
    """
    Audit log for machine learning model training, validation, and evaluation metrics.
    """
    model_name = models.CharField(max_length=100)
    target_variable = models.CharField(max_length=100)
    prediction_horizon = models.CharField(max_length=100, default='Next Semester')
    sample_size = models.PositiveIntegerField(default=0)
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    roc_auc = models.FloatField(null=True, blank=True)
    baseline_accuracy = models.FloatField(null=True, blank=True, help_text=_("Majority class baseline"))
    confusion_matrix = models.JSONField(default=dict)
    feature_importances = models.JSONField(default=dict)
    trained_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-trained_at']
        verbose_name = _('Model Evaluation Result')
        verbose_name_plural = _('Model Evaluation Results')

    def __str__(self):
        f1_str = f"F1: {self.f1_score:.2f}" if self.f1_score is not None else "No F1"
        return f"{self.model_name} on {self.target_variable} ({f1_str}) at {self.trained_at:%Y-%m-%d}"
