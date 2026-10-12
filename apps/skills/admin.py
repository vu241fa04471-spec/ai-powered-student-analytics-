from django.contrib import admin
from apps.skills.models import SkillCategory, Skill, StudentSkillAssessment

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(StudentSkillAssessment)
class StudentSkillAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'skill', 'proficiency_level', 'score', 'assessment_date')
    list_filter = ('proficiency_level', 'skill__category')
    search_fields = ('student__student_id', 'skill__name')
