from django.contrib import admin
from apps.attendance.models import AttendanceSession, AttendanceRecord, SubjectAttendanceSummary

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'faculty', 'session_date', 'session_type', 'semester', 'section')
    list_filter = ('session_type', 'session_date', 'subject', 'semester')
    search_fields = ('subject__code', 'subject__name', 'faculty__username')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status')
    list_filter = ('status', 'session__subject')
    search_fields = ('student__student_id', 'student__user__first_name', 'session__subject__code')


@admin.register(SubjectAttendanceSummary)
class SubjectAttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'semester', 'classes_attended', 'total_classes', 'attendance_percentage', 'is_shortage')
    list_filter = ('is_shortage', 'semester', 'subject')
    search_fields = ('student__student_id', 'subject__code')
