"""
Deterministic rule-based Student Segmentation Engine.
Classifies students into Segments A through F based on multi-dimensional academic,
attendance, engagement, and placement competencies.
"""

from decimal import Decimal
from apps.analytics.models import StudentSegment, ScoreTier, RiskLevel, PlacementReadinessStatus
from apps.analytics.services.scoring_engine import StudentSuccessScoreEngine
from apps.analytics.services.risk_engine import AcademicRiskEngine
from apps.analytics.services.placement_engine import PlacementAnalyticsEngine

SEGMENT_DEFINITIONS = {
    'SEGMENT_A': {
        'name': 'Segment A: Strong Academics, Low Placement Readiness',
        'code': 'SEG_A_ACAD_STRONG_PLACE_LOW',
        'description': 'Students with solid grade performance who face technical coding, aptitude, or interview readiness deficits.',
        'criteria': 'CGPA >= 7.0 AND Placement Readiness Score < 55.0',
        'recommended_action': 'Targeted coding bootcamps, aptitude drills, mock interview coaching, and resume ATS overhaul.',
        'badge_color': '#F59E0B', # Amber/Warning
    },
    'SEGMENT_B': {
        'name': 'Segment B: Good Academics, Poor Attendance',
        'code': 'SEG_B_GOOD_ACAD_POOR_ATTEND',
        'description': 'Academically capable students who have fallen below the mandatory 75% attendance threshold.',
        'criteria': 'CGPA >= 6.5 AND Aggregate Attendance < 75%',
        'recommended_action': 'Faculty mentor outreach, schedule conflict review, and attendance recovery contract.',
        'badge_color': '#EC4899', # Pink
    },
    'SEGMENT_C': {
        'name': 'Segment C: At-Risk Academic Performance',
        'code': 'SEG_C_ACADEMIC_RISK',
        'description': 'Students experiencing active course backlogs, steep SGPA drops, or critical GPA deficits.',
        'criteria': 'Academic Risk HIGH or CRITICAL OR Active Backlogs > 0 OR CGPA < 6.0',
        'recommended_action': 'Remedial academic tutoring, backlog clearance plan, and bi-weekly mentor check-ins.',
        'badge_color': '#EF4444', # Red
    },
    'SEGMENT_D': {
        'name': 'Segment D: Strong Overall Performance',
        'code': 'SEG_D_HIGH_PERFORMERS',
        'description': 'Top-tier achievers across academics, attendance, digital engagement, and placement benchmarks.',
        'criteria': 'Success Score >= 85.0 AND Completeness >= 70% AND Risk Level is LOW',
        'recommended_action': 'Fast-track research opportunities, peer-tutoring leadership, and Tier-1 corporate mentorship.',
        'badge_color': '#10B981', # Green
    },
    'SEGMENT_E': {
        'name': 'Segment E: Low Digital Engagement',
        'code': 'SEG_E_LOW_ENGAGEMENT',
        'description': 'Students with consistently poor LMS platform logins, missed deadlines, or digital platform disengagement.',
        'criteria': 'LMS Engagement Score < 50.0 AND Evidence Completeness >= 50%',
        'recommended_action': 'Digital access barrier audit, course coordinator check-in, and deadline management guidance.',
        'badge_color': '#8B5CF6', # Purple
    },
    'SEGMENT_F': {
        'name': 'Segment F: Insufficient Data',
        'code': 'SEG_F_INSUFFICIENT_DATA',
        'description': 'Students lacking sufficient verified records to make reliable automated risk or success assessments.',
        'criteria': 'Evidence Completeness < 40.0%',
        'recommended_action': 'Verify institutional data integration feeds and schedule baseline diagnostic assessments.',
        'badge_color': '#64748B', # Slate
    },
}

class StudentSegmentationEngine:
    def __init__(self):
        self.scoring_engine = StudentSuccessScoreEngine()
        self.risk_engine = AcademicRiskEngine()
        self.placement_engine = PlacementAnalyticsEngine()

    def get_or_create_segments(self):
        """
        Ensures all 6 standard segments exist in the database.
        """
        segment_objs = {}
        for key, conf in SEGMENT_DEFINITIONS.items():
            seg, _ = StudentSegment.objects.update_or_create(
                code=conf['code'],
                defaults={
                    'name': conf['name'],
                    'description': conf['description'],
                    'criteria_summary': conf['criteria'],
                    'badge_color': conf['badge_color'],
                }
            )
            segment_objs[key] = seg
        return segment_objs

    def classify_student(self, student):
        """
        Evaluates deterministic membership rules for a student.
        Returns a list of matching segment keys.
        """
        score_eval = self.scoring_engine.evaluate_student(student)
        risk_eval = self.risk_engine.assess_student(student)
        place_eval = self.placement_engine.assess_student(student)

        matched_segments = []
        completeness = score_eval['data_completeness']

        # Segment F: Insufficient Data check first
        if completeness < Decimal('40.0'):
            matched_segments.append('SEGMENT_F')
            return matched_segments  # Avoid contradictory classifications

        cgpa = Decimal(str(student.get_latest_cgpa()))
        attendance_pct = Decimal(str(student.get_overall_attendance_percentage()))
        placement_score = place_eval['readiness_score']
        composite_score = score_eval['composite_score']
        lms_score = score_eval['component_scores']['lms']
        backlogs = student.get_active_backlogs_count()

        # Segment A: Strong Academics, Low Placement Readiness
        if cgpa >= Decimal('7.0') and (placement_score < Decimal('55.0') or place_eval['readiness_status'] in [PlacementReadinessStatus.BORDERLINE, PlacementReadinessStatus.AT_RISK]):
            matched_segments.append('SEGMENT_A')

        # Segment B: Good Academics, Poor Attendance
        if cgpa >= Decimal('6.5') and attendance_pct < Decimal('75.0'):
            matched_segments.append('SEGMENT_B')

        # Segment C: At-Risk Academic Performance
        if risk_eval['risk_level'] in [RiskLevel.HIGH, RiskLevel.CRITICAL] or backlogs > 0 or cgpa < Decimal('6.0'):
            matched_segments.append('SEGMENT_C')

        # Segment D: Strong Overall Performance
        if composite_score >= Decimal('85.0') and completeness >= Decimal('70.0') and risk_eval['risk_level'] == RiskLevel.LOW:
            matched_segments.append('SEGMENT_D')

        # Segment E: Low Engagement
        if lms_score < Decimal('50.0') and completeness >= Decimal('50.0'):
            matched_segments.append('SEGMENT_E')

        return matched_segments

    def sync_student_segments(self, student):
        """
        Updates database ManyToMany relationships for student segments.
        """
        segment_objs = self.get_or_create_segments()
        matched_keys = self.classify_student(student)

        # Clear old memberships and assign current matches
        for key, seg in segment_objs.items():
            if key in matched_keys:
                seg.students.add(student)
            else:
                seg.students.remove(student)

        return matched_keys
