from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from apps.accounts.models import Role, User
from apps.students.models import StudentProfile, Department, Semester
from apps.academics.models import AcademicRecord, BacklogRecord
from apps.attendance.models import SubjectAttendanceSummary
from apps.lms.models import LMSEngagementSummary
from apps.analytics.models import AcademicRiskAssessment, StudentSuccessSnapshot, RiskIndicator
from apps.interventions.models import InterventionRecord, InterventionRecommendation
from apps.placements.models import PlacementCompany, PlacementApplication, ResumeReadiness

@login_required
def dashboard_view(request):
    user = request.user

    # STUDENT DASHBOARD
    if user.is_student_role:
        student = getattr(user, 'student_profile', None)
        if not student:
            return render(request, 'dashboard/no_profile.html')

        academic_records = student.academic_records.order_by('-semester__number')
        latest_academic = academic_records.first()
        attendance_summaries = student.attendance_summaries.all()
        overall_attendance = student.get_overall_attendance_percentage()
        active_backlogs = student.get_active_backlogs_count()

        latest_success = student.success_snapshots.order_by('-snapshot_date').first()
        risk_indicators = student.risk_indicators.filter(is_resolved=False).order_by('-detected_at')[:5]
        recommendations = student.intervention_recommendations.filter(
            status__in=['PROPOSED', 'APPROVED', 'IN_PROGRESS']
        ).order_by('-created_at')[:5]
        latest_lms = student.lms_summaries.order_by('-semester__number').first()

        context = {
            'student': student,
            'latest_academic': latest_academic,
            'academic_records': academic_records,
            'attendance_summaries': attendance_summaries,
            'overall_attendance': overall_attendance,
            'active_backlogs': active_backlogs,
            'latest_success': latest_success,
            'risk_indicators': risk_indicators,
            'recommendations': recommendations,
            'latest_lms': latest_lms,
        }
        return render(request, 'dashboard/student_dashboard.html', context)

    # FACULTY DASHBOARD
    elif user.is_faculty_role:
        dept = user.department
        students_qs = StudentProfile.objects.filter(department=dept) if dept else StudentProfile.objects.none()
        total_dept_students = students_qs.count()

        mentored_students = user.mentored_students.select_related('current_semester')
        
        # Risk counts in faculty's department
        dept_high_risks = AcademicRiskAssessment.objects.filter(
            student__in=students_qs,
            risk_level__in=['HIGH', 'CRITICAL']
        ).select_related('student__user').order_by('-risk_probability')[:8]

        attendance_shortages = SubjectAttendanceSummary.objects.filter(
            student__in=students_qs,
            is_shortage=True
        ).count()

        active_interventions = InterventionRecord.objects.filter(
            assigned_to=user,
            status='ACTIVE'
        ).count()

        context = {
            'department': dept,
            'total_dept_students': total_dept_students,
            'mentored_count': mentored_students.count(),
            'mentored_students': mentored_students[:5],
            'dept_high_risks': dept_high_risks,
            'attendance_shortages': attendance_shortages,
            'active_interventions': active_interventions,
        }
        return render(request, 'dashboard/faculty_dashboard.html', context)

    # PLACEMENT OFFICER DASHBOARD
    elif user.is_placement_officer_role:
        total_students = StudentProfile.objects.count()
        tier_ready_count = StudentSuccessSnapshot.objects.filter(placement_score__gte=75).count()
        upcoming_companies = PlacementCompany.objects.order_by('drive_date')[:5]
        total_offers = PlacementApplication.objects.filter(status='OFFERED').count()
        resume_needs_work = ResumeReadiness.objects.filter(readiness_level='NEEDS_WORK').count()

        context = {
            'total_students': total_students,
            'tier_ready_count': tier_ready_count,
            'upcoming_companies': upcoming_companies,
            'total_offers': total_offers,
            'resume_needs_work': resume_needs_work,
        }
        return render(request, 'dashboard/placement_dashboard.html', context)

    # ADMINISTRATOR / DEFAULT DASHBOARD
    else:
        total_students = StudentProfile.objects.count()
        total_faculty = User.objects.filter(role=Role.FACULTY).count()
        departments_count = Department.objects.count()

        # Risk distribution
        high_risk_count = AcademicRiskAssessment.objects.filter(risk_level__in=['HIGH', 'CRITICAL']).count()
        active_interventions_count = InterventionRecord.objects.filter(status='ACTIVE').count()
        attendance_shortage_count = SubjectAttendanceSummary.objects.filter(is_shortage=True).count()

        # Department metrics
        departments = Department.objects.annotate(
            student_count=Count('students')
        )

        recent_risks = AcademicRiskAssessment.objects.select_related(
            'student__user', 'student__department'
        ).order_by('-assessed_at')[:8]

        recent_indicators = RiskIndicator.objects.filter(
            is_resolved=False
        ).select_related('student__user').order_by('-detected_at')[:8]

        context = {
            'total_students': total_students,
            'total_faculty': total_faculty,
            'departments_count': departments_count,
            'high_risk_count': high_risk_count,
            'active_interventions_count': active_interventions_count,
            'attendance_shortage_count': attendance_shortage_count,
            'departments': departments,
            'recent_risks': recent_risks,
            'recent_indicators': recent_indicators,
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
