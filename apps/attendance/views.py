from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.attendance.models import SubjectAttendanceSummary
from apps.accounts.permissions import get_authorized_students_queryset

@login_required
def attendance_shortage_list_view(request):
    """
    Shows students with attendance shortage (< 75%) within authorized scope.
    """
    allowed_students = get_authorized_students_queryset(request.user)
    shortages = SubjectAttendanceSummary.objects.filter(
        student__in=allowed_students,
        is_shortage=True
    ).select_related('student__user', 'student__department', 'subject', 'semester').order_by('attendance_percentage')

    return render(request, 'attendance/shortage_list.html', {
        'shortages': shortages,
    })
