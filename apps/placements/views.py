from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.placements.models import PlacementCompany, PlacementApplication, ResumeReadiness
from apps.accounts.permissions import get_authorized_students_queryset

@login_required
def placement_overview_view(request):
    companies = PlacementCompany.objects.all().order_by('-drive_date')
    allowed_students = get_authorized_students_queryset(request.user)
    applications = PlacementApplication.objects.filter(
        student__in=allowed_students
    ).select_related('student__user', 'company').order_by('-application_date')

    return render(request, 'placements/placement_overview.html', {
        'companies': companies,
        'applications': applications,
    })
