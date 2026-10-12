from django.contrib import admin
from apps.engagement.models import Club, ExtracurricularEvent, StudentParticipation, Certification

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'faculty_coordinator', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)


@admin.register(ExtracurricularEvent)
class ExtracurricularEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'club', 'event_date', 'organized_by')
    list_filter = ('event_type', 'event_date')
    search_fields = ('title', 'organized_by')


@admin.register(StudentParticipation)
class StudentParticipationAdmin(admin.ModelAdmin):
    list_display = ('student', 'event', 'role', 'verified')
    list_filter = ('role', 'verified')
    search_fields = ('student__student_id', 'event__title')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'issuing_organization', 'issue_date', 'verified')
    list_filter = ('issuing_organization', 'verified')
    search_fields = ('student__student_id', 'title')
