"""
Actionable Intervention Recommendation engine.
Generates advisory, transparent support recommendations triggered by verified indicators and rule conditions.
"""

from decimal import Decimal
import datetime
from django.utils import timezone
from apps.interventions.models import (
    InterventionRecommendation, InterventionCategory, InterventionPriority, RecommendationStatus
)

class InterventionRecommendationEngine:
    def generate_recommendations_for_student(self, student):
        """
        Evaluates student performance across all pillars and proposes actionable interventions.
        Idempotent: Avoids duplicate pending recommendations for the same issue.
        """
        proposed_list = []
        today = datetime.date.today()
        follow_up_target = today + datetime.timedelta(days=14)

        # 1. Attendance Shortage Trigger
        overall_att = student.get_overall_attendance_percentage()
        if overall_att < 60.0:
            proposed_list.append({
                "category": InterventionCategory.ATTENDANCE_COUNSELING,
                "priority": InterventionPriority.URGENT,
                "title": "Immediate Attendance Counseling & Examination Debarment Warning",
                "description": f"Overall attendance sits at {overall_att:.1f}%, far below the 75% statutory requirement. Immediate parental notification and mentor counseling required.",
                "trigger_indicator": "attendance_critical",
            })
        elif overall_att < 75.0:
            proposed_list.append({
                "category": InterventionCategory.ATTENDANCE_COUNSELING,
                "priority": InterventionPriority.HIGH,
                "title": "Attendance Recovery Contract & Class Timetable Review",
                "description": f"Student has dropped to {overall_att:.1f}% attendance. A structured make-up class plan is advised to avoid end-term debarment.",
                "trigger_indicator": "attendance_shortage",
            })

        # 2. Backlog Trigger
        active_backlogs = student.get_active_backlogs_count()
        if active_backlogs > 0:
            priority = InterventionPriority.URGENT if active_backlogs >= 2 else InterventionPriority.HIGH
            proposed_list.append({
                "category": InterventionCategory.ACADEMIC_TUTORING,
                "priority": priority,
                "title": f"Academic Recovery Plan for {active_backlogs} Active Backlog Course(s)",
                "description": f"Student has {active_backlogs} uncleared backlog(s). Subject-matter faculty tutoring and remedial assignment schedule recommended.",
                "trigger_indicator": "active_backlogs",
            })

        # 3. CGPA & Trajectory Trigger
        records = list(student.academic_records.order_by('semester__number'))
        if len(records) >= 2:
            prev_sgpa = records[-2].sgpa
            curr_sgpa = records[-1].sgpa
            drop = prev_sgpa - curr_sgpa
            if drop >= Decimal('0.75'):
                proposed_list.append({
                    "category": InterventionCategory.MENTOR_MEETING,
                    "priority": InterventionPriority.HIGH,
                    "title": f"Grade Collapse Advisory Session (-{drop:.2f} SGPA Delta)",
                    "description": f"SGPA dropped from {prev_sgpa} to {curr_sgpa}. Schedule an in-person advisory check-in to identify personal or conceptual roadblocks.",
                    "trigger_indicator": "sgpa_drop",
                })

        # 4. Placement Readiness & Coding Deficit
        coding = student.coding_assessments.order_by('-assessment_date').first()
        if coding and coding.score < Decimal('50.0'):
            proposed_list.append({
                "category": InterventionCategory.CODING_BOOTCAMP,
                "priority": InterventionPriority.HIGH,
                "title": "Fast-Track Algorithmic Coding Bootcamp & LeetCode Practice",
                "description": f"Coding assessment score ({coding.score:.1f}/100) indicates high risk of elimination in first-round company screening tests.",
                "trigger_indicator": "low_coding_score",
            })

        # 5. Mock Interview / Communication Deficit
        mock = student.mock_interviews.order_by('-interview_date').first()
        if mock and mock.overall_score < Decimal('50.0'):
            proposed_list.append({
                "category": InterventionCategory.MOCK_INTERVIEW_PREP,
                "priority": InterventionPriority.MEDIUM,
                "title": "Interview Simulation & Technical Communication Coaching",
                "description": f"Mock interview score ({mock.overall_score:.1f}/100) shows gaps in technical articulation. Schedule 1-on-1 interview practice.",
                "trigger_indicator": "low_mock_interview",
            })

        # 6. LMS Digital Inactivity
        latest_lms = student.lms_summaries.order_by('-semester__number').first()
        if latest_lms and latest_lms.assignments_missed >= 2:
            proposed_list.append({
                "category": InterventionCategory.MENTOR_MEETING,
                "priority": InterventionPriority.MEDIUM,
                "title": "Digital Courseware & Assignment Submission Deadline Support",
                "description": f"Student missed {latest_lms.assignments_missed} course assignments this term. Check for hardware/connectivity or time management constraints.",
                "trigger_indicator": "lms_missed_assignments",
            })

        # Persist generated recommendations without duplicates
        created_records = []
        for prop in proposed_list:
            existing = InterventionRecommendation.objects.filter(
                student=student,
                title=prop["title"],
                status__in=[RecommendationStatus.PROPOSED, RecommendationStatus.APPROVED, RecommendationStatus.IN_PROGRESS]
            ).first()

            if not existing:
                rec = InterventionRecommendation.objects.create(
                    student=student,
                    title=prop["title"],
                    description=prop["description"],
                    category=prop["category"],
                    priority=prop["priority"],
                    generated_by_ai=True,
                    status=RecommendationStatus.PROPOSED,
                )
                created_records.append(rec)

        return created_records
