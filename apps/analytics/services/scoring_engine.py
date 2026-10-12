"""
Transparent, multi-dimensional Student Success Score calculation engine.
Includes configurable grading scales, indicators, normalization, and missing-data re-weighting.
"""

from decimal import Decimal, ROUND_HALF_UP
import datetime
from django.db.models import Avg, Sum
from apps.analytics.models import StudentSuccessSnapshot, ScoreTier, PerformanceTrend, ConfidenceLevel
from apps.analytics.services.config import (
    DEFAULT_WEIGHTS, DEFAULT_GRADING_SCALE, DATA_QUALITY_POLICY, SCORING_VERSION
)

class StudentSuccessScoreEngine:
    def __init__(self, weights=None, grading_scale=None):
        self.weights = weights or DEFAULT_WEIGHTS
        self.grading_scale = grading_scale or DEFAULT_GRADING_SCALE

    def compute_academic_component(self, student):
        """
        Calculates academic score (0-100) based on CGPA and backlog adjustment.
        Returns (score, is_available, details).
        """
        latest_academic = student.academic_records.order_by('-semester__number').first()
        if not latest_academic or latest_academic.cgpa is None:
            return None, False, {"reason": "No academic record found"}

        max_cgpa = self.grading_scale.get('max_cgpa', Decimal('10.0'))
        raw_cgpa = latest_academic.cgpa
        
        # Base normalized score
        normalized_cgpa = min(Decimal('100.0'), max(Decimal('0.0'), (raw_cgpa / max_cgpa) * Decimal('100.0')))
        
        # Backlog deduction (each active backlog reduces academic score by 5 points)
        active_backlogs = student.get_active_backlogs_count()
        backlog_penalty = Decimal(str(active_backlogs * 5.0))
        final_academic_score = max(Decimal('0.0'), normalized_cgpa - backlog_penalty)

        details = {
            "cgpa": float(raw_cgpa),
            "max_scale": float(max_cgpa),
            "normalized_cgpa": float(normalized_cgpa),
            "active_backlogs": active_backlogs,
            "backlog_penalty": float(backlog_penalty),
            "raw_score": float(final_academic_score)
        }
        return final_academic_score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), True, details

    def compute_attendance_component(self, student):
        """
        Calculates attendance score (0-100) from validated subject summaries.
        Returns (score, is_available, details).
        """
        summaries = student.attendance_summaries.all()
        if not summaries.exists():
            return None, False, {"reason": "No attendance records recorded"}

        total_classes = sum(s.total_classes for s in summaries)
        attended_classes = sum(s.classes_attended for s in summaries)

        if total_classes == 0:
            return Decimal('100.0'), True, {"total_classes": 0, "attended_classes": 0, "attendance_pct": 100.0}

        att_pct = (Decimal(str(attended_classes)) / Decimal(str(total_classes))) * Decimal('100.0')
        att_pct = min(Decimal('100.0'), max(Decimal('0.0'), att_pct))

        details = {
            "total_conducted": total_classes,
            "total_attended": attended_classes,
            "overall_pct": float(att_pct)
        }
        return att_pct.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), True, details

    def compute_lms_component(self, student):
        """
        Calculates LMS digital engagement (0-100) from summary or submissions.
        Returns (score, is_available, details).
        """
        latest_lms = student.lms_summaries.order_by('-semester__number').first()
        if not latest_lms:
            # Check individual assignment submissions
            submissions = student.assignment_submissions.all()
            if not submissions.exists():
                return None, False, {"reason": "No LMS digital activity recorded"}
            
            total_subs = submissions.count()
            on_time = submissions.filter(status='ON_TIME').count()
            score = (Decimal(str(on_time)) / Decimal(str(total_subs))) * Decimal('100.0')
            return score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), True, {"submissions_count": total_subs}

        score = latest_lms.lms_engagement_score
        details = {
            "total_logins": latest_lms.total_logins,
            "assignments_completed": latest_lms.assignments_completed,
            "assignments_late": latest_lms.assignments_late,
            "assignments_missed": latest_lms.assignments_missed,
            "resources_accessed": latest_lms.resources_accessed_count
        }
        return score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), True, details

    def compute_extracurricular_component(self, student):
        """
        Calculates extracurricular engagement (0-100).
        Rewards participations, wins, leadership roles, and certifications with reasonable caps.
        Returns (score, is_available, details).
        """
        participations = student.event_participations.select_related('event')
        certifications = student.certifications.filter(verified=True)

        part_count = participations.count()
        cert_count = certifications.count()

        if part_count == 0 and cert_count == 0:
            # Extracurricular is considered neutral/available with baseline 50 if student is enrolled,
            # but if no activities logged at all, we return 50.0 (baseline neutral) or mark available.
            return Decimal('50.0'), True, {"participations": 0, "certifications": 0, "status": "Baseline neutral"}

        score = Decimal('50.0')  # Base level
        for p in participations:
            if p.role in ['WINNER', 'LEADER']:
                score += Decimal('15.0')
            elif p.role == 'RUNNER_UP':
                score += Decimal('10.0')
            elif p.role in ['ORGANIZER', 'PARTICIPANT']:
                score += Decimal('6.0')

        score += Decimal(str(cert_count * 10.0))
        capped_score = min(Decimal('100.0'), score)

        details = {
            "participations_count": part_count,
            "certifications_count": cert_count,
            "calculated_score": float(capped_score)
        }
        return capped_score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), True, details

    def compute_placement_component(self, student):
        """
        Calculates placement readiness (0-100) from aptitude, coding, mock interviews, and ATS score.
        Returns (score, is_available, details).
        """
        coding = student.coding_assessments.order_by('-assessment_date').first()
        aptitude = student.aptitude_assessments.order_by('-test_date').first()
        mock = student.mock_interviews.order_by('-interview_date').first()
        resume = getattr(student, 'resume_readiness', None)

        available_subscores = []
        details = {}

        if coding:
            available_subscores.append(coding.score)
            details["coding_score"] = float(coding.score)
        if aptitude and aptitude.max_score > 0:
            apt_pct = (aptitude.total_score / aptitude.max_score) * Decimal('100.0')
            available_subscores.append(apt_pct)
            details["aptitude_score"] = float(apt_pct)
        if mock:
            available_subscores.append(mock.overall_score)
            details["mock_interview_score"] = float(mock.overall_score)
        if resume:
            available_subscores.append(Decimal(str(resume.ats_score)))
            details["resume_ats_score"] = resume.ats_score

        if not available_subscores:
            return None, False, {"reason": "No placement evaluations or assessments recorded"}

        avg_score = sum(available_subscores) / Decimal(str(len(available_subscores)))
        return avg_score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), True, details

    def compute_skills_component(self, student):
        """
        Calculates verified technical and soft skill benchmarks (0-100).
        Returns (score, is_available, details).
        """
        assessments = student.skill_assessments.all()
        if not assessments.exists():
            return None, False, {"reason": "No skill assessments recorded"}

        avg_score = assessments.aggregate(avg=Avg('score'))['avg']
        if avg_score is None:
            return None, False, {"reason": "No valid skill scores"}

        score = Decimal(str(avg_score))
        return score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), True, {"skills_assessed_count": assessments.count()}

    def evaluate_student(self, student):
        """
        Calculates the complete Student Success Score with transparent missing-data re-weighting.
        """
        computations = {
            'academic': self.compute_academic_component(student),
            'attendance': self.compute_attendance_component(student),
            'lms': self.compute_lms_component(student),
            'extracurricular': self.compute_extracurricular_component(student),
            'placement': self.compute_placement_component(student),
            'skills': self.compute_skills_component(student),
        }

        component_scores = {}
        available_indicators = []
        missing_indicators = []
        total_available_weight = Decimal('0.0')
        weighted_sum = Decimal('0.0')
        breakdown_details = {}

        for dim, (score, is_avail, details) in computations.items():
            breakdown_details[dim] = details
            if is_avail and score is not None:
                component_scores[dim] = score
                available_indicators.append(dim)
                dim_weight = self.weights[dim]
                total_available_weight += dim_weight
                weighted_sum += (score * dim_weight)
            else:
                component_scores[dim] = Decimal('0.0')
                missing_indicators.append(dim)

        # Data completeness percentage
        total_configured_weight = sum(self.weights.values())
        data_completeness = (total_available_weight / total_configured_weight) * Decimal('100.0')
        data_completeness = data_completeness.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Determine confidence level
        if data_completeness >= DATA_QUALITY_POLICY['high_confidence_threshold']:
            confidence_level = ConfidenceLevel.HIGH
        elif data_completeness >= DATA_QUALITY_POLICY['medium_confidence_threshold']:
            confidence_level = ConfidenceLevel.MEDIUM
        elif data_completeness >= DATA_QUALITY_POLICY['low_confidence_threshold']:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.INSUFFICIENT

        is_insufficient = (data_completeness < DATA_QUALITY_POLICY['min_completeness_for_score'])

        # Compute re-weighted composite score: weighted_sum / total_available_weight
        if total_available_weight > 0 and not is_insufficient:
            composite_score = (weighted_sum / total_available_weight).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Score Tier
            if composite_score >= 85:
                score_tier = ScoreTier.EXCELLENT
            elif composite_score >= 70:
                score_tier = ScoreTier.GOOD
            elif composite_score >= 55:
                score_tier = ScoreTier.AVERAGE
            else:
                score_tier = ScoreTier.AT_RISK
        else:
            composite_score = Decimal('0.0')
            score_tier = ScoreTier.INSUFFICIENT

        # Calculate exact linear contribution of each indicator
        contributions = {}
        positive_drivers = []
        negative_drivers = []

        for dim in available_indicators:
            dim_score = component_scores[dim]
            # Exact formula: (weight * score) / total_available_weight
            contrib = (self.weights[dim] * dim_score / total_available_weight).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            contributions[dim] = float(contrib)
            
            if dim_score >= Decimal('75.0'):
                positive_drivers.append({"dimension": dim, "score": float(dim_score), "contribution": float(contrib)})
            elif dim_score < Decimal('60.0'):
                negative_drivers.append({"dimension": dim, "score": float(dim_score), "contribution": float(contrib)})

        # Determine trend based on previous snapshots
        previous_snapshot = student.success_snapshots.order_by('-snapshot_date').first()
        if previous_snapshot and not is_insufficient:
            delta = composite_score - previous_snapshot.composite_success_score
            if delta > Decimal('2.0'):
                trend = PerformanceTrend.IMPROVING
            elif delta < Decimal('-2.0'):
                trend = PerformanceTrend.DECLINING
            else:
                trend = PerformanceTrend.STABLE
        else:
            trend = PerformanceTrend.STABLE

        full_breakdown = {
            "component_scores": {k: float(v) for k, v in component_scores.items()},
            "configured_weights": {k: float(v) for k, v in self.weights.items()},
            "contributions": contributions,
            "total_available_weight": float(total_available_weight),
            "data_completeness_pct": float(data_completeness),
            "positive_drivers": positive_drivers,
            "negative_drivers": negative_drivers,
            "dimension_details": breakdown_details,
            "scoring_version": SCORING_VERSION,
        }

        return {
            "composite_score": composite_score,
            "score_tier": score_tier,
            "confidence_level": confidence_level,
            "data_completeness": data_completeness,
            "is_insufficient_data": is_insufficient,
            "trend": trend,
            "component_scores": component_scores,
            "available_indicators": available_indicators,
            "missing_indicators": missing_indicators,
            "breakdown": full_breakdown,
        }

    def save_snapshot(self, student):
        """
        Idempotently generates or updates a StudentSuccessSnapshot for today.
        Avoids duplicate snapshot rows on identical days.
        """
        eval_result = self.evaluate_student(student)
        today = datetime.date.today()

        snapshot, created = StudentSuccessSnapshot.objects.update_or_create(
            student=student,
            snapshot_date=today,
            defaults={
                "academic_score": eval_result["component_scores"]["academic"],
                "attendance_score": eval_result["component_scores"]["attendance"],
                "engagement_score": eval_result["component_scores"]["lms"],
                "extracurricular_score": eval_result["component_scores"]["extracurricular"],
                "placement_score": eval_result["component_scores"]["placement"],
                "skills_score": eval_result["component_scores"]["skills"],
                "composite_success_score": eval_result["composite_score"],
                "score_tier": eval_result["score_tier"],
                "trend": eval_result["trend"],
                "data_completeness": eval_result["data_completeness"],
                "confidence_level": eval_result["confidence_level"],
                "is_insufficient_data": eval_result["is_insufficient_data"],
                "available_indicators": eval_result["available_indicators"],
                "missing_indicators": eval_result["missing_indicators"],
                "score_breakdown": eval_result["breakdown"],
                "scoring_version": SCORING_VERSION,
            }
        )
        return snapshot
