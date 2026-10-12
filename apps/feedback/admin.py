from django.contrib import admin
from apps.feedback.models import FeedbackCategory, StudentFeedback, FacultyFeedback

@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(StudentFeedback)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ('category', 'satisfaction_score', 'semester', 'is_anonymous', 'created_at')
    list_filter = ('category', 'satisfaction_score', 'is_anonymous')
    search_fields = ('comments',)


@admin.register(FacultyFeedback)
class FacultyFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'faculty', 'academic_aptitude_rating', 'discipline_attendance_rating', 'semester', 'created_at')
    list_filter = ('academic_aptitude_rating', 'discipline_attendance_rating', 'semester')
    search_fields = ('student__student_id', 'faculty__username')
