from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class AptitudeAssessment(models.Model):
    """
    Quantitative, logical, and verbal reasoning scores.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='aptitude_assessments'
    )
    test_name = models.CharField(max_length=150)
    quantitative_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    logical_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    verbal_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    test_date = models.DateField()

    class Meta:
        ordering = ['-test_date']
        verbose_name = _('Aptitude Assessment')
        verbose_name_plural = _('Aptitude Assessments')

    def __str__(self):
        return f"{self.student.student_id} - {self.test_name}: {self.total_score}/{self.max_score}"


class CodingAssessment(models.Model):
    """
    Technical coding tests and platform performance.
    """
    PLATFORM_CHOICES = [
        ('INTERNAL', _('Campus Assessment Portal')),
        ('HACKERRANK', _('HackerRank')),
        ('LEETCODE', _('LeetCode')),
        ('CODECHEF', _('CodeChef')),
    ]

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='coding_assessments'
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='INTERNAL')
    problems_attempted = models.PositiveSmallIntegerField(default=0)
    problems_solved = models.PositiveSmallIntegerField(default=0)
    score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    programming_languages = models.CharField(max_length=100, default='Python, Java, C++')
    assessment_date = models.DateField()

    class Meta:
        ordering = ['-assessment_date']
        verbose_name = _('Coding Assessment')
        verbose_name_plural = _('Coding Assessments')

    def __str__(self):
        return f"{self.student.student_id} Coding: {self.score}/100 ({self.platform})"


class MockInterview(models.Model):
    """
    Faculty and industry expert mock interview evaluations.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='mock_interviews'
    )
    interviewer_name = models.CharField(max_length=150)
    technical_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    communication_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    behavioral_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    overall_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    feedback_notes = models.TextField(blank=True)
    interview_date = models.DateField()

    class Meta:
        ordering = ['-interview_date']
        verbose_name = _('Mock Interview')
        verbose_name_plural = _('Mock Interviews')

    def __str__(self):
        return f"{self.student.student_id} Mock Interview: {self.overall_score}/100"


class ResumeReadiness(models.Model):
    """
    Resume audit score and project portfolio readiness.
    """
    LEVEL_CHOICES = [
        ('NEEDS_WORK', _('Needs Immediate Work (< 50 ATS)')),
        ('ADEQUATE', _('Adequate (50-70 ATS)')),
        ('READY', _('Job Ready (70-85 ATS)')),
        ('EXCEPTIONAL', _('Exceptional Portfolio (85+ ATS)')),
    ]

    student = models.OneToOneField(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='resume_readiness'
    )
    ats_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=60
    )
    projects_count = models.PositiveSmallIntegerField(default=1)
    internships_count = models.PositiveSmallIntegerField(default=0)
    readiness_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='ADEQUATE')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_resumes'
    )
    review_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _('Resume Readiness')
        verbose_name_plural = _('Resume Readiness Records')

    def __str__(self):
        return f"{self.student.student_id} Resume ATS: {self.ats_score}% ({self.get_readiness_level_display()})"


class PlacementCompany(models.Model):
    """
    Recruiting company visiting campus.
    """
    name = models.CharField(max_length=150, unique=True)
    industry = models.CharField(max_length=100)
    drive_date = models.DateField()
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=6.5)
    allowed_backlogs = models.PositiveSmallIntegerField(default=0)
    package_lpa = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text=_("Annual package in Lakhs Per Annum (LPA)")
    )

    class Meta:
        ordering = ['-drive_date']
        verbose_name = _('Placement Company')
        verbose_name_plural = _('Placement Companies')

    def __str__(self):
        return f"{self.name} ({self.package_lpa} LPA)"


class PlacementApplication(models.Model):
    """
    Student job drive applications and outcomes.
    """
    STATUS_CHOICES = [
        ('APPLIED', _('Applied')),
        ('SHORTLISTED', _('Shortlisted')),
        ('ASSESSMENT_CLEARED', _('Assessment Cleared')),
        ('INTERVIEW_SCHEDULED', _('Interview Scheduled')),
        ('OFFERED', _('Job Offer Received')),
        ('REJECTED', _('Not Selected')),
    ]

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='placement_applications'
    )
    company = models.ForeignKey(
        PlacementCompany,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='APPLIED')
    package_offered_lpa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    offer_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'company')
        ordering = ['-application_date']
        verbose_name = _('Placement Application')
        verbose_name_plural = _('Placement Applications')

    def __str__(self):
        return f"{self.student.student_id} -> {self.company.name} ({self.status})"
