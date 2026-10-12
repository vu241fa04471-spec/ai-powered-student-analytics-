from django.contrib import admin
from apps.lms.models import LMSActivity, LMSAssignmentSubmission, LMSQuizAttempt, LMSEngagementSummary

@admin.register(LMSActivity)
class LMSActivityAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity_type', 'timestamp', 'duration_minutes')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('student__student_id', 'student__user__username')


@admin.register(LMSAssignmentSubmission)
class LMSAssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'title', 'due_date', 'submitted_at', 'status', 'score')
    list_filter = ('status', 'subject')
    search_fields = ('student__student_id', 'title')


@admin.register(LMSQuizAttempt)
class LMSQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'quiz_title', 'score', 'total_score', 'attempted_at')
    list_filter = ('subject',)
    search_fields = ('student__student_id', 'quiz_title')


@admin.register(LMSEngagementSummary)
class LMSEngagementSummaryAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'total_logins', 'assignments_completed', 'assignments_missed', 'lms_engagement_score')
    list_filter = ('semester',)
    search_fields = ('student__student_id',)
