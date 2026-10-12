"""
Central configuration for Smart Campus Analytics scoring models, thresholds, and grading scales.
All parameters are decoupled and easily configurable by institutions.
"""

from decimal import Decimal

# 1. Component Indicator Weights (Sum = 1.00)
DEFAULT_WEIGHTS = {
    'academic': Decimal('0.30'),
    'attendance': Decimal('0.20'),
    'lms': Decimal('0.15'),
    'extracurricular': Decimal('0.10'),
    'placement': Decimal('0.15'),
    'skills': Decimal('0.10'),
}

# 2. Grading Scale Normalization
DEFAULT_GRADING_SCALE = {
    'scale_type': '10_POINT',
    'max_cgpa': Decimal('10.0'),
    'min_pass_cgpa': Decimal('4.0'),
}

# 3. Academic Risk Thresholds
ACADEMIC_RISK_THRESHOLDS = {
    'attendance_critical': Decimal('60.0'),
    'attendance_warning': Decimal('75.0'),
    'cgpa_critical': Decimal('5.0'),
    'cgpa_warning': Decimal('6.0'),
    'sgpa_consecutive_drop': Decimal('0.75'),
    'backlogs_critical': 2,
    'backlogs_warning': 1,
    'missed_assignments_critical': 3,
    'missed_assignments_warning': 2,
}

# 4. Placement Readiness Thresholds
PLACEMENT_THRESHOLDS = {
    'tier_1_score': Decimal('80.0'),
    'ready_score': Decimal('65.0'),
    'borderline_score': Decimal('50.0'),
    'resume_ats_warning': 50,
    'coding_score_warning': Decimal('50.0'),
    'mock_interview_warning': Decimal('50.0'),
}

# 5. Missing Data & Confidence Policy
DATA_QUALITY_POLICY = {
    'min_completeness_for_score': Decimal('40.0'),  # Below 40% -> INSUFFICIENT
    'high_confidence_threshold': Decimal('80.0'),   # >= 80% -> HIGH
    'medium_confidence_threshold': Decimal('60.0'), # 60 - 79% -> MEDIUM
    'low_confidence_threshold': Decimal('40.0'),    # 40 - 59% -> LOW
}

# 6. Scoring Rule Version
SCORING_VERSION = "v2.0-transparent-weighted"
