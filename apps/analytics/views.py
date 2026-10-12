from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.accounts.permissions import get_authorized_students_queryset, role_required
from apps.accounts.models import Role
from apps.analytics.models import AcademicRiskAssessment, RiskIndicator, StudentSegment, StudentSuccessSnapshot

@login_required
def risk_dashboard_view(request):
    """
    Overview of students needing academic support or intervention.
    """
    allowed_students = get_authorized_students_queryset(request.user)

    # Risk level distribution
    critical_risks = AcademicRiskAssessment.objects.filter(
        student__in=allowed_students,
        risk_level__in=['HIGH', 'CRITICAL']
    ).select_related('student__user', 'student__department', 'student__current_semester').order_by('-risk_probability')

    unresolved_indicators = RiskIndicator.objects.filter(
        student__in=allowed_students,
        is_resolved=False
    ).select_related('student__user').order_by('-detected_at')[:20]

    segments = StudentSegment.objects.all()

    return render(request, 'analytics/risk_dashboard.html', {
        'critical_risks': critical_risks,
        'unresolved_indicators': unresolved_indicators,
        'segments': segments,
    })


@login_required
def segments_view(request):
    segments = StudentSegment.objects.prefetch_related('students__user', 'students__department').all()
    return render(request, 'analytics/segments.html', {'segments': segments})
