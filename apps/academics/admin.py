from django.contrib import admin
from apps.academics.models import Subject, AcademicRecord, AssessmentResult, BacklogRecord

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'semester_number', 'credits', 'is_elective')
    list_filter = ('department', 'semester_number', 'is_elective')
    search_fields = ('code', 'name')


@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'sgpa', 'cgpa', 'credits_earned', 'cumulative_backlogs', 'status')
    list_filter = ('semester', 'status')
    search_fields = ('student__student_id', 'student__user__first_name', 'student__user__last_name')


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'assessment_type', 'marks_obtained', 'max_marks', 'assessment_date')
    list_filter = ('assessment_type', 'semester', 'subject')
    search_fields = ('student__student_id', 'subject__code', 'subject__name')


@admin.register(BacklogRecord)
class BacklogRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'semester_failed', 'status', 'attempts_count', 'cleared_date')
    list_filter = ('status', 'semester_failed')
    search_fields = ('student__student_id', 'subject__code')
