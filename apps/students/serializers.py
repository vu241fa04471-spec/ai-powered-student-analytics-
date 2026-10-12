from rest_framework import serializers
from apps.students.models import StudentProfile, Department, Program, Semester
from apps.academics.models import AcademicRecord, Subject
from apps.attendance.models import SubjectAttendanceSummary
from apps.analytics.models import StudentSuccessSnapshot, AcademicRiskAssessment, RiskIndicator

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'established_year']


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['id', 'code', 'name', 'degree_type', 'total_semesters']


class AcademicRecordSerializer(serializers.ModelSerializer):
    semester_number = serializers.IntegerField(source='semester.number', read_only=True)

    class Meta:
        model = AcademicRecord
        fields = [
            'id', 'semester_number', 'sgpa', 'cgpa',
            'credits_registered', 'credits_earned',
            'backlogs_in_semester', 'cumulative_backlogs', 'status'
        ]


class SubjectAttendanceSummarySerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = SubjectAttendanceSummary
        fields = [
            'id', 'subject_code', 'subject_name',
            'total_classes', 'classes_attended',
            'attendance_percentage', 'is_shortage'
        ]


class RiskIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskIndicator
        fields = [
            'id', 'category', 'title', 'details',
            'severity', 'is_resolved', 'detected_at'
        ]


class StudentSuccessSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSuccessSnapshot
        fields = [
            'id', 'snapshot_date', 'academic_score', 'attendance_score',
            'engagement_score', 'placement_score', 'composite_success_score',
            'score_tier', 'trend', 'score_breakdown'
        ]


class AcademicRiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicRiskAssessment
        fields = [
            'id', 'assessed_at', 'risk_level', 'risk_probability',
            'predicted_outcome', 'key_drivers', 'model_version'
        ]


class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    semester_number = serializers.IntegerField(source='current_semester.number', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'student_id', 'full_name', 'email',
            'department', 'department_name',
            'program', 'program_name',
            'semester_number', 'section',
            'enrollment_status', 'admission_year',
            'expected_graduation_year'
        ]
