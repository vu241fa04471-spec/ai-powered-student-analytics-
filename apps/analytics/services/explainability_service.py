"""
Explainable AI (XAI) service for Student Success Scores and Risk Assessments.
Provides mathematical attribution of linear weights, exact feature contributions,
and auditable risk rule triggers without fabrication.
"""

from decimal import Decimal

class ScoringExplainabilityService:
    @staticmethod
    def explain_success_score(snapshot_or_eval):
        """
        Decomposes a student success score into exact linear contributions,
        weights, positive drivers, negative drivers, and confidence disclosures.
        """
        breakdown = snapshot_or_eval.get("breakdown") if isinstance(snapshot_or_eval, dict) else snapshot_or_eval.score_breakdown
        comp_scores = breakdown.get("component_scores", {})
        weights = breakdown.get("configured_weights", {})
        contributions = breakdown.get("contributions", {})
        total_avail_weight = breakdown.get("total_available_weight", 1.0)
        completeness = breakdown.get("data_completeness_pct", 100.0)

        explanation = {
            "title": "Transparent Multi-Factor Attribution",
            "scoring_formula": "Success Score = sum(weight_i * score_i) / sum(weight_i)",
            "total_available_weight": total_avail_weight,
            "data_completeness_percentage": completeness,
            "factor_explanations": [],
            "positive_drivers": breakdown.get("positive_drivers", []),
            "negative_drivers": breakdown.get("negative_drivers", []),
            "legal_and_fairness_disclosure": (
                "Notice: This score is an explainable decision-support indicator designed to assist academic mentors. "
                "Correlations identified by the system do not represent causal proof. Consequential actions require human review."
            )
        }

        dim_labels = {
            "academic": "Academic Performance (CGPA & Backlogs)",
            "attendance": "Classroom Attendance Rate",
            "lms": "Digital Platform & LMS Engagement",
            "extracurricular": "Extracurricular & Certifications",
            "placement": "Placement Assessment Readiness",
            "skills": "Verified Skill Proficiency",
        }

        for dim, score in comp_scores.items():
            dim_weight = weights.get(dim, 0.0)
            contrib = contributions.get(dim, 0.0)
            explanation["factor_explanations"].append({
                "dimension": dim,
                "label": dim_labels.get(dim, dim.title()),
                "observed_score": score,
                "configured_weight_pct": round(dim_weight * 100, 1),
                "exact_point_contribution": contrib,
                "is_observed": score > 0 or dim not in breakdown.get("missing_indicators", [])
            })

        return explanation

    @staticmethod
    def explain_risk_assessment(assessment_or_eval):
        """
        Provides human-readable audit trail of triggered risk rules,
        observed values vs statutory thresholds, and severity ratings.
        """
        factors = assessment_or_eval.get("risk_factors") if isinstance(assessment_or_eval, dict) else assessment_or_eval.risk_factors
        level = assessment_or_eval.get("risk_level") if isinstance(assessment_or_eval, dict) else assessment_or_eval.risk_level

        return {
            "risk_level": level,
            "triggered_rules_count": len(factors),
            "audit_trail": factors,
            "mitigation_advice": (
                "All identified risks are advisory early warnings. Faculty mentors should review context with the student "
                "before taking formal administrative action."
            )
        }
