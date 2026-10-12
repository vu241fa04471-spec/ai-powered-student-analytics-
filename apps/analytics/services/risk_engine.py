"""
Academic Risk Assessment engine with interpretable, rule-based auditing.
Evaluates attendance deficits, backlogs, grade trajectory, and digital engagement.
"""

from decimal import Decimal
import datetime
from django.utils import timezone
from apps.analytics.models import AcademicRiskAssessment, RiskLevel, RiskIndicator, RiskSeverity
from apps.analytics.services.config import ACADEMIC_RISK_THRESHOLDS, DATA_QUALITY_POLICY

class AcademicRiskEngine:
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or ACADEMIC_RISK_THRESHOLDS

    def assess_student(self, student):
        """
        Runs comprehensive rule-based evaluation of academic risk factors.
        Returns a structured dictionary with risk category, score, and factors.
        """
        risk_factors = []
        key_drivers = []
        severity_points = Decimal('0.0')
        evaluated_metrics_count = 0

        # 1. Attendance Evaluation
        overall_att = student.get_overall_attendance_percentage()
        evaluated_metrics_count += 1
        att_dec = Decimal(str(overall_att))

        if att_dec < self.thresholds['attendance_critical']:
            risk_factors.append({
                "indicator": "attendance_critical",
                "label": "Severe Attendance Deficit (< 60%)",
                "observed_value": float(att_dec),
                "threshold": float(self.thresholds['attendance_critical']),
                "severity": "CRITICAL",
                "impact_score": 35.0,
                "reason": "Statutory exam debarment imminent due to attendance below 60%"
            })
            key_drivers.append({"factor": "Critical Attendance Deficit", "impact": -35})
            severity_points += Decimal('35.0')
        elif att_dec < self.thresholds['attendance_warning']:
            risk_factors.append({
                "indicator": "attendance_warning",
                "label": "Attendance Shortage (< 75%)",
                "observed_value": float(att_dec),
                "threshold": float(self.thresholds['attendance_warning']),
                "severity": "WARNING",
                "impact_score": 20.0,
                "reason": "Attendance falls below university minimum 75% criterion"
            })
            key_drivers.append({"factor": "Attendance Shortage", "impact": -20})
            severity_points += Decimal('20.0')

        # 2. Backlogs Evaluation
        active_backlogs = student.get_active_backlogs_count()
        evaluated_metrics_count += 1

        if active_backlogs >= self.thresholds['backlogs_critical']:
            risk_factors.append({
                "indicator": "backlogs_critical",
                "label": f"Multiple Active Backlogs ({active_backlogs})",
                "observed_value": active_backlogs,
                "threshold": self.thresholds['backlogs_critical'],
                "severity": "CRITICAL",
                "impact_score": 30.0,
                "reason": f"Accumulation of {active_backlogs} uncleared courses risks graduation delay"
            })
            key_drivers.append({"factor": "Multiple Course Backlogs", "impact": -30})
            severity_points += Decimal('30.0')
        elif active_backlogs >= self.thresholds['backlogs_warning']:
            risk_factors.append({
                "indicator": "backlogs_warning",
                "label": f"Active Course Backlog ({active_backlogs})",
                "observed_value": active_backlogs,
                "threshold": self.thresholds['backlogs_warning'],
                "severity": "WARNING",
                "impact_score": 15.0,
                "reason": "Active backlog requires remedial clearance"
            })
            key_drivers.append({"factor": "Active Course Backlog", "impact": -15})
            severity_points += Decimal('15.0')

        # 3. CGPA & Trajectory Evaluation
        academic_records = list(student.academic_records.order_by('semester__number'))
        if academic_records:
            evaluated_metrics_count += 1
            latest_rec = academic_records[-1]
            cgpa = latest_rec.cgpa

            if cgpa < self.thresholds['cgpa_critical']:
                risk_factors.append({
                    "indicator": "cgpa_critical",
                    "label": "Critical Academic Standing (CGPA < 5.0)",
                    "observed_value": float(cgpa),
                    "threshold": float(self.thresholds['cgpa_critical']),
                    "severity": "CRITICAL",
                    "impact_score": 25.0,
                    "reason": "Cumulative GPA below minimum retention benchmark"
                })
                key_drivers.append({"factor": "Critical GPA Level", "impact": -25})
                severity_points += Decimal('25.0')
            elif cgpa < self.thresholds['cgpa_warning']:
                risk_factors.append({
                    "indicator": "cgpa_warning",
                    "label": "Low Academic Performance (CGPA < 6.0)",
                    "observed_value": float(cgpa),
                    "threshold": float(self.thresholds['cgpa_warning']),
                    "severity": "WARNING",
                    "impact_score": 15.0,
                    "reason": "CGPA is on warning watchlist (< 6.0)"
                })
                key_drivers.append({"factor": "Low Cumulative GPA", "impact": -15})
                severity_points += Decimal('15.0')

            # Trajectory check: Did SGPA drop consecutively by >= 0.75 points?
            if len(academic_records) >= 2:
                prev_sgpa = academic_records[-2].sgpa
                curr_sgpa = latest_rec.sgpa
                drop = prev_sgpa - curr_sgpa
                if drop >= self.thresholds['sgpa_consecutive_drop']:
                    risk_factors.append({
                        "indicator": "sgpa_drop",
                        "label": f"Steep Grade Point Drop (-{drop:.2f})",
                        "observed_value": float(drop),
                        "threshold": float(self.thresholds['sgpa_consecutive_drop']),
                        "severity": "WARNING",
                        "impact_score": 15.0,
                        "reason": f"SGPA collapsed from {prev_sgpa} to {curr_sgpa}"
                    })
                    key_drivers.append({"factor": "Steep Semester SGPA Drop", "impact": -15})
                    severity_points += Decimal('15.0')

        # 4. LMS Assignment Timeliness
        latest_lms = student.lms_summaries.order_by('-semester__number').first()
        if latest_lms:
            evaluated_metrics_count += 1
            if latest_lms.assignments_missed >= self.thresholds['missed_assignments_critical']:
                risk_factors.append({
                    "indicator": "lms_missed_assignments",
                    "label": f"Repeated Assignment Failures ({latest_lms.assignments_missed} Missed)",
                    "observed_value": latest_lms.assignments_missed,
                    "threshold": self.thresholds['missed_assignments_critical'],
                    "severity": "WARNING",
                    "impact_score": 10.0,
                    "reason": "Failure to complete multiple continuous learning assessments"
                })
                key_drivers.append({"factor": "Multiple Missed Assignments", "impact": -10})
                severity_points += Decimal('10.0')

        # Evidence Completeness
        completeness = Decimal(str(min(100.0, (evaluated_metrics_count / 4.0) * 100.0)))

        # Determine Final Risk Category
        if completeness < DATA_QUALITY_POLICY['min_completeness_for_score']:
            risk_level = RiskLevel.INSUFFICIENT
            risk_score = Decimal('0.0')
            predicted_outcome = "Insufficient Evidence for Academic Assessment"
            calibrated_probability = 0.0
        else:
            risk_score = min(Decimal('100.0'), severity_points)
            calibrated_probability = round(min(0.98, max(0.02, float(risk_score) / 100.0)), 2)

            # Categorization logic
            critical_count = sum(1 for f in risk_factors if f['severity'] == 'CRITICAL')
            if critical_count >= 1 or risk_score >= Decimal('55.0'):
                risk_level = RiskLevel.CRITICAL
                predicted_outcome = "Immediate Risk of Academic Probation or Debarment"
            elif risk_score >= Decimal('30.0'):
                risk_level = RiskLevel.HIGH
                predicted_outcome = "High Vulnerability to Course Failure"
            elif risk_score >= Decimal('15.0'):
                risk_level = RiskLevel.MEDIUM
                predicted_outcome = "Academic Watchlist Monitoring"
            else:
                risk_level = RiskLevel.LOW
                predicted_outcome = "On-Track for Successful Graduation"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_probability": calibrated_probability,
            "predicted_outcome": predicted_outcome,
            "key_drivers": key_drivers,
            "risk_factors": risk_factors,
            "evidence_completeness": completeness,
            "model_version": "v2.0-explainable-rules",
        }

    def save_assessment(self, student):
        """
        Idempotently persists the AcademicRiskAssessment and syncs active RiskIndicator rows.
        """
        result = self.assess_student(student)

        assessment = AcademicRiskAssessment.objects.create(
            student=student,
            risk_level=result["risk_level"],
            risk_score=result["risk_score"],
            risk_probability=result["risk_probability"],
            predicted_outcome=result["predicted_outcome"],
            key_drivers=result["key_drivers"],
            risk_factors=result["risk_factors"],
            evidence_completeness=result["evidence_completeness"],
            model_version=result["model_version"],
        )

        # Sync active RiskIndicator records
        now = timezone.now()
        for factor in result["risk_factors"]:
            sev = RiskSeverity.CRITICAL if factor['severity'] == 'CRITICAL' else RiskSeverity.WARNING
            cat = "ATTENDANCE" if "attendance" in factor['indicator'] else "ACADEMIC"
            RiskIndicator.objects.get_or_create(
                student=student,
                title=factor["label"],
                defaults={
                    "category": cat,
                    "details": factor["reason"],
                    "severity": sev,
                    "is_resolved": False,
                }
            )

        return assessment
