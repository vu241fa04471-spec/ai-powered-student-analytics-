from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class SkillCategory(models.Model):
    """
    Skill taxonomy domain (Programming, DevOps, Soft Skills, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Skill Category')
        verbose_name_plural = _('Skill Categories')

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Individual technical or behavioral skill.
    """
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['category', 'name']
        unique_together = ('category', 'name')
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class ProficiencyLevel(models.TextChoices):
    BEGINNER = 'BEGINNER', _('Beginner (Level 1)')
    INTERMEDIATE = 'INTERMEDIATE', _('Intermediate (Level 2)')
    ADVANCED = 'ADVANCED', _('Advanced (Level 3)')
    EXPERT = 'EXPERT', _('Expert / Production Ready (Level 4)')


class StudentSkillAssessment(models.Model):
    """
    Student skill proficiency rating.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='skill_assessments'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='student_assessments'
    )
    proficiency_level = models.CharField(
        max_length=20,
        choices=ProficiencyLevel.choices,
        default=ProficiencyLevel.INTERMEDIATE
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text=_("Standardized skill benchmark score (0 - 100)")
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_skills'
    )
    assessment_date = models.DateField()

    class Meta:
        unique_together = ('student', 'skill')
        ordering = ['student', '-score']
        verbose_name = _('Student Skill Assessment')
        verbose_name_plural = _('Student Skill Assessments')

    def __str__(self):
        return f"{self.student.student_id} - {self.skill.name}: {self.score}/100 ({self.get_proficiency_level_display()})"
