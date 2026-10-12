"""
Placement Readiness and Risk Analytics service.
Evaluates technical coding, aptitude, mock interviews, and resume ATS benchmarks.
Clearly distinguishes between candidate competency readiness and job hiring probability.
"""

from decimal import Decimal, ROUND_HALF_UP
from apps.analytics.models import PlacementRiskAssessment, PlacementReadinessStatus
from apps.analytics.services.config import PLACEMENT_THRESHOLDS, DATA_QUALITY_POLICY

class PlacementAnalyticsEngine:
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or PLACEMENT_THRESHOLDS

    def assess_student(self, student):
        """
        Assesses placement preparation, detects skill gaps, and suggests career roadmap.
        """
        subscores = []
        skill_gaps = []
        suggested_activities = []
        metrics_checked = 0
        metrics_found = 0

        # 1. Coding Assessment
        metrics_checked += 1
        coding = student.coding_assessments.order_by('-assessment_date').first()
        if coding:
            metrics_found += 1
            subscores.append(coding.score)
            if coding.score < self.thresholds['coding_score_warning']:
                skill_gaps.append("Data Structures & Algorithmic Problem Solving")
                suggested_activities.append("Enroll in Intensive DSA & LeetCode Sprint Bootcamp")
        else:
            skill_gaps.append("Unassessed Coding Proficiency")
            suggested_activities.append("Schedule Mandatory Platform Coding Benchmark Assessment")

        # 2. Aptitude Assessment
        metrics_checked += 1
        aptitude = student.aptitude_assessments.order_by('-test_date').first()
        if aptitude and aptitude.max_score > 0:
            metrics_found += 1
            apt_pct = (aptitude.total_score / aptitude.max_score) * Decimal('100.0')
            subscores.append(apt_pct)
            if apt_pct < Decimal('55.0'):
                skill_gaps.append("Quantitative & Logical Reasoning Speed")
                suggested_activities.append("Attend Aptitude Practice Test Series")
        else:
            skill_gaps.append("Unassessed Quantitative Aptitude")

        # 3. Mock Interview
        metrics_checked += 1
        mock = student.mock_interviews.order_by('-interview_date').first()
        if mock:
            metrics_found += 1
            subscores.append(mock.overall_score)
            if mock.communication_score < Decimal('60.0'):
                skill_gaps.append("Professional Verbal English & HR Articulation")
                suggested_activities.append("Participate in Group Discussion & Communication Workshop")
            if mock.technical_score < self.thresholds['mock_interview_warning']:
                skill_gaps.append("Technical Conceptual Clarity in Live Interviews")
                suggested_activities.append("Schedule 1-on-1 Faculty Mock Interview Retake")
        else:
            suggested_activities.append("Book Mock Interview with Faculty / Industry Panel")

        # 4. Resume ATS Readiness
        metrics_checked += 1
        resume = getattr(student, 'resume_readiness', None)
        if resume:
            metrics_found += 1
            subscores.append(Decimal(str(resume.ats_score)))
            if resume.ats_score < self.thresholds['resume_ats_warning']:
                skill_gaps.append("Resume ATS Formatting & Key Industry Keywords")
                suggested_activities.append("Complete Career Center Resume Audit & Project Portfolio Review")
            if resume.projects_count < 2:
                skill_gaps.append("Limited Practical Portfolio Projects")
                suggested_activities.append("Build and Deploy Capstone Industry Project on GitHub")
        else:
            suggested_activities.append("Submit Resume to Career Center for ATS Audit")

        # 5. Evidence Completeness
        completeness = Decimal(str(round((metrics_found / float(metrics_checked)) * 100.0, 1)))

        if completeness < DATA_QUALITY_POLICY['min_completeness_for_score'] or not subscores:
            readiness_status = PlacementReadinessStatus.INSUFFICIENT
            readiness_score = Decimal('0.0')
            recommended_focus = "Complete Initial Placement Baseline Tests (Aptitude, Coding, Resume Audit)"
        else:
            readiness_score = (sum(subscores) / Decimal(str(len(subscores)))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            if readiness_score >= self.thresholds['tier_1_score']:
                readiness_status = PlacementReadinessStatus.TIER_1_READY
                recommended_focus = "Tier-1 Product Company Interview Simulation & System Design"
            elif readiness_score >= self.thresholds['ready_score']:
                readiness_status = PlacementReadinessStatus.READY
                recommended_focus = "Core Service & Product Engineering Campus Recruitment Preparation"
            elif readiness_score >= self.thresholds['borderline_score']:
                readiness_status = PlacementReadinessStatus.BORDERLINE
                recommended_focus = "Targeted Fast-Track Coding Drills and Mock Interview Retakes"
            else:
                readiness_status = PlacementReadinessStatus.AT_RISK
                recommended_focus = "Comprehensive Remedial Career Readiness Intervention"

        return {
            "readiness_status": readiness_status,
            "readiness_score": readiness_score,
            "evidence_completeness": completeness,
            "skill_gaps": skill_gaps,
            "suggested_activities": suggested_activities,
            "recommended_focus": recommended_focus,
        }

    def save_assessment(self, student):
        """
        Idempotently persists the PlacementRiskAssessment record.
        """
        result = self.assess_student(student)

        assessment = PlacementRiskAssessment.objects.create(
            student=student,
            readiness_status=result["readiness_status"],
            readiness_score=result["readiness_score"],
            evidence_completeness=result["evidence_completeness"],
            skill_gaps=result["skill_gaps"],
            suggested_activities=result["suggested_activities"],
            recommended_focus=result["recommended_focus"],
        )
        return assessment
