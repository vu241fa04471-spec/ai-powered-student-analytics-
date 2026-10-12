from django.contrib import admin
from apps.analytics.models import (
    StudentSuccessSnapshot, AcademicRiskAssessment,
    PlacementRiskAssessment, RiskIndicator, StudentSegment,
    ModelEvaluationResult
)

@admin.register(StudentSuccessSnapshot)
class StudentSuccessSnapshotAdmin(admin.ModelAdmin):
    list_display = ('student', 'composite_success_score', 'score_tier', 'confidence_level', 'data_completeness', 'trend', 'snapshot_date')
    list_filter = ('score_tier', 'confidence_level', 'is_insufficient_data', 'trend', 'snapshot_date')
    search_fields = ('student__student_id', 'student__user__first_name', 'student__user__last_name')


@admin.register(AcademicRiskAssessment)
class AcademicRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'risk_level', 'risk_score', 'risk_probability', 'predicted_outcome', 'model_version', 'assessed_at')
    list_filter = ('risk_level', 'model_version')
    search_fields = ('student__student_id',)


@admin.register(PlacementRiskAssessment)
class PlacementRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'readiness_status', 'readiness_score', 'evidence_completeness', 'assessed_at')
    list_filter = ('readiness_status',)
    search_fields = ('student__student_id',)


@admin.register(RiskIndicator)
class RiskIndicatorAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'category', 'severity', 'is_resolved', 'detected_at')
    list_filter = ('category', 'severity', 'is_resolved')
    search_fields = ('student__student_id', 'title')


@admin.register(StudentSegment)
class StudentSegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'badge_color')
    search_fields = ('name', 'code')
    filter_horizontal = ('students',)


@admin.register(ModelEvaluationResult)
class ModelEvaluationResultAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'target_variable', 'accuracy', 'f1_score', 'roc_auc', 'baseline_accuracy', 'trained_at')
    list_filter = ('model_name', 'target_variable')
    search_fields = ('model_name', 'target_variable')
