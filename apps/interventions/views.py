from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.permissions import get_authorized_students_queryset, role_required
from apps.accounts.models import Role
from apps.interventions.models import InterventionRecord, InterventionRecommendation, InterventionFollowUp
from apps.students.models import StudentProfile

@login_required
def intervention_list_view(request):
    """
    List active interventions within authorized user scope.
    """
    allowed_students = get_authorized_students_queryset(request.user)

    interventions = InterventionRecord.objects.filter(
        student__in=allowed_students
    ).select_related('student__user', 'student__department', 'assigned_to').order_by('-start_date')

    status_filter = request.GET.get('status')
    if status_filter:
        interventions = interventions.filter(status=status_filter)

    recommendations = InterventionRecommendation.objects.filter(
        student__in=allowed_students,
        status='PROPOSED'
    ).select_related('student__user').order_by('-created_at')[:10]

    return render(request, 'interventions/intervention_list.html', {
        'interventions': interventions,
        'recommendations': recommendations,
        'selected_status': status_filter or '',
    })
