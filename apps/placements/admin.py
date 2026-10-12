from django.contrib import admin
from apps.placements.models import (
    AptitudeAssessment, CodingAssessment, MockInterview,
    ResumeReadiness, PlacementCompany, PlacementApplication
)

@admin.register(AptitudeAssessment)
class AptitudeAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'test_name', 'quantitative_score', 'logical_score', 'verbal_score', 'total_score', 'test_date')
    list_filter = ('test_date',)
    search_fields = ('student__student_id', 'test_name')


@admin.register(CodingAssessment)
class CodingAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'platform', 'problems_solved', 'score', 'assessment_date')
    list_filter = ('platform', 'assessment_date')
    search_fields = ('student__student_id',)


@admin.register(MockInterview)
class MockInterviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'interviewer_name', 'technical_score', 'communication_score', 'overall_score', 'interview_date')
    list_filter = ('interview_date',)
    search_fields = ('student__student_id', 'interviewer_name')


@admin.register(ResumeReadiness)
class ResumeReadinessAdmin(admin.ModelAdmin):
    list_display = ('student', 'ats_score', 'projects_count', 'internships_count', 'readiness_level', 'review_date')
    list_filter = ('readiness_level',)
    search_fields = ('student__student_id',)


@admin.register(PlacementCompany)
class PlacementCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'package_lpa', 'min_cgpa', 'allowed_backlogs', 'drive_date')
    list_filter = ('industry', 'drive_date')
    search_fields = ('name',)


@admin.register(PlacementApplication)
class PlacementApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'status', 'package_offered_lpa', 'application_date')
    list_filter = ('status', 'company')
    search_fields = ('student__student_id', 'company__name')
