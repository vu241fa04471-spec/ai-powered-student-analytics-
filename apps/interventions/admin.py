from django.contrib import admin
from apps.interventions.models import (
    InterventionRecommendation, InterventionRecord,
    InterventionFollowUp, InterventionOutcome
)

@admin.register(InterventionRecommendation)
class InterventionRecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'category', 'priority', 'status', 'generated_by_ai', 'created_at')
    list_filter = ('category', 'priority', 'status', 'generated_by_ai')
    search_fields = ('student__student_id', 'title')


@admin.register(InterventionRecord)
class InterventionRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'intervention_type', 'assigned_to', 'status', 'start_date', 'target_completion_date')
    list_filter = ('status', 'assigned_to')
    search_fields = ('student__student_id', 'intervention_type')


@admin.register(InterventionFollowUp)
class InterventionFollowUpAdmin(admin.ModelAdmin):
    list_display = ('intervention', 'recorded_by', 'follow_up_date', 'impact_assessment')
    list_filter = ('impact_assessment', 'follow_up_date')
    search_fields = ('intervention__student__student_id',)


@admin.register(InterventionOutcome)
class InterventionOutcomeAdmin(admin.ModelAdmin):
    list_display = ('intervention', 'outcome_status', 'pre_metric_value', 'post_metric_value', 'closed_at')
    list_filter = ('outcome_status',)
