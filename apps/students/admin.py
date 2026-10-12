from django.contrib import admin
from apps.students.models import Department, Program, AcademicYear, Semester, StudentProfile, FacultyAssignment

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'head_of_department', 'established_year')
    search_fields = ('code', 'name')


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'degree_type', 'total_semesters', 'is_active')
    list_filter = ('department', 'degree_type', 'is_active')
    search_fields = ('code', 'name')


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('number', 'term', 'academic_year', 'is_current', 'start_date', 'end_date')
    list_filter = ('academic_year', 'term', 'is_current')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'department', 'program', 'current_semester', 'section', 'enrollment_status', 'admission_year')
    list_filter = ('department', 'program', 'current_semester', 'enrollment_status', 'admission_year')
    search_fields = ('student_id', 'user__first_name', 'user__last_name', 'user__username', 'user__email')
    raw_id_fields = ('user', 'mentor')


@admin.register(FacultyAssignment)
class FacultyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'subject', 'semester', 'section', 'academic_year')
    list_filter = ('academic_year', 'semester', 'section')
    search_fields = ('faculty__username', 'faculty__first_name', 'faculty__last_name', 'subject__name', 'subject__code')
