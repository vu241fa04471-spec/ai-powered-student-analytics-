from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.academics.models import Subject, AcademicRecord
from apps.accounts.permissions import get_authorized_students_queryset

@login_required
def subjects_list_view(request):
    subjects = Subject.objects.select_related('department').all().order_by('department', 'semester_number', 'code')
    dept_id = request.GET.get('department')
    if dept_id:
        subjects = subjects.filter(department_id=dept_id)
    return render(request, 'academics/subjects_list.html', {'subjects': subjects})
