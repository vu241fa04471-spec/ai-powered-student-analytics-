from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Club(models.Model):
    """
    Student societies, technical clubs, and sports teams.
    """
    CATEGORY_CHOICES = [
        ('TECHNICAL', _('Technical / Coding / Robotics')),
        ('CULTURAL', _('Cultural / Arts / Music')),
        ('SPORTS', _('Sports & Athletics')),
        ('SOCIAL_SERVICE', _('Social Service / NSS / Rotaract')),
        ('ENTREPRENEURSHIP', _('E-Cell / Innovation')),
    ]

    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='TECHNICAL')
    description = models.TextField(blank=True)
    faculty_coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_clubs'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Student Club')
        verbose_name_plural = _('Student Clubs')

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ExtracurricularEvent(models.Model):
    """
    Hackathons, workshops, conferences, and competitions.
    """
    EVENT_TYPES = [
        ('HACKATHON', _('Hackathon')),
        ('WORKSHOP', _('Technical Workshop')),
        ('SEMINAR', _('Guest Lecture / Seminar')),
        ('COMPETITION', _('Coding / Project Competition')),
        ('SPORTS', _('Sports Tournament')),
        ('CULTURAL', _('Cultural Fest')),
    ]

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='WORKSHOP')
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    organized_by = models.CharField(max_length=150)
    event_date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-event_date']
        verbose_name = _('Extracurricular Event')
        verbose_name_plural = _('Extracurricular Events')

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()}, {self.event_date})"


class ParticipationRole(models.TextChoices):
    PARTICIPANT = 'PARTICIPANT', _('Participant')
    ORGANIZER = 'ORGANIZER', _('Student Coordinator / Organizer')
    LEADER = 'LEADER', _('Team Lead')
    WINNER = 'WINNER', _('Winner (1st Place)')
    RUNNER_UP = 'RUNNER_UP', _('Runner Up (2nd/3rd Place)')


class StudentParticipation(models.Model):
    """
    Student participation record in events.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='event_participations'
    )
    event = models.ForeignKey(
        ExtracurricularEvent,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    role = models.CharField(
        max_length=20,
        choices=ParticipationRole.choices,
        default=ParticipationRole.PARTICIPANT
    )
    award_details = models.CharField(max_length=200, blank=True)
    verified = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'event')
        ordering = ['-event__event_date']
        verbose_name = _('Student Participation')
        verbose_name_plural = _('Student Participations')

    def __str__(self):
        return f"{self.student.student_id} in {self.event.title} as {self.get_role_display()}"


class Certification(models.Model):
    """
    Industry and online professional certifications.
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    title = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=150)
    issue_date = models.DateField()
    credential_url = models.URLField(blank=True)
    verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['-issue_date']
        verbose_name = _('Certification')
        verbose_name_plural = _('Certifications')

    def __str__(self):
        return f"{self.student.student_id} - {self.title} ({self.issuing_organization})"
