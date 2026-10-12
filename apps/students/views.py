from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import models
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.students.models import StudentProfile, Department, Semester
from apps.accounts.permissions import get_authorized_students_queryset, can_user_access_student

class StudentListView(LoginRequiredMixin, ListView):
    model = StudentProfile
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        qs = get_authorized_students_queryset(self.request.user)
        qs = qs.select_related('user', 'department', 'program', 'current_semester')

        # Filters
        dept_id = self.request.GET.get('department')
        if dept_id:
            qs = qs.filter(department_id=dept_id)

        sem_id = self.request.GET.get('semester')
        if sem_id:
            qs = qs.filter(current_semester_id=sem_id)

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(enrollment_status=status)

        search_query = self.request.GET.get('q')
        if search_query:
            qs = qs.filter(
                models.Q(student_id__icontains=search_query) |
                models.Q(user__first_name__icontains=search_query) |
                models.Q(user__last_name__icontains=search_query)
            )

        return qs.order_by('student_id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departments'] = Department.objects.all()
        ctx['semesters'] = Semester.objects.filter(is_current=True)
        ctx['selected_dept'] = self.request.GET.get('department', '')
        ctx['selected_sem'] = self.request.GET.get('semester', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


@login_required
def student_detail_view(request, student_id):
    student = get_object_or_404(StudentProfile.objects.select_related(
        'user', 'department', 'program', 'current_semester', 'mentor'
    ), student_id=student_id)

    # Server-side security check
    if not can_user_access_student(request.user, student):
        raise PermissionDenied("You do not have permission to view this student profile.")

    # Fetch related records for comprehensive profile view
    academic_records = student.academic_records.select_related('semester').order_by('semester__number')
    attendance_summaries = student.attendance_summaries.select_related('subject', 'semester')
    lms_summary = getattr(student, 'lms_summaries', None)
    latest_lms = student.lms_summaries.order_by('-semester__number').first() if hasattr(student, 'lms_summaries') else None
    
    # Analytics snapshots & risk indicators
    risk_assessment = student.academic_risk_assessments.order_by('-assessed_at').first() if hasattr(student, 'academic_risk_assessments') else None
    placement_assessment = student.placement_risk_assessments.order_by('-assessed_at').first() if hasattr(student, 'placement_risk_assessments') else None
    risk_indicators = student.risk_indicators.filter(is_resolved=False).order_by('-detected_at')[:10] if hasattr(student, 'risk_indicators') else []
    success_snapshot = student.success_snapshots.order_by('-snapshot_date').first() if hasattr(student, 'success_snapshots') else None

    # Interventions
    interventions = student.intervention_records.select_related('assigned_to').order_by('-start_date') if hasattr(student, 'intervention_records') else []

    # Placements
    placement_applications = student.placement_applications.select_related('company').order_by('-application_date') if hasattr(student, 'placement_applications') else []

    return render(request, 'students/student_detail.html', {
        'student': student,
        'academic_records': academic_records,
        'attendance_summaries': attendance_summaries,
        'latest_lms': latest_lms,
        'risk_assessment': risk_assessment,
        'placement_assessment': placement_assessment,
        'risk_indicators': risk_indicators,
        'success_snapshot': success_snapshot,
        'interventions': interventions,
        'placement_applications': placement_applications,
    })
