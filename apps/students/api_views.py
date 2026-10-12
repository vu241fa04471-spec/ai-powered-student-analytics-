from rest_framework import viewsets, permissions
from apps.students.models import StudentProfile, Department, Program
from apps.students.serializers import (
    StudentProfileSerializer, DepartmentSerializer, ProgramSerializer
)
from apps.accounts.permissions import (
    get_authorized_students_queryset, CanAccessStudentDataDRF, IsAdminRole
)

class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Student Profiles with strict data scoping.
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessStudentDataDRF]
    filterset_fields = ['department', 'program', 'enrollment_status', 'section']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['student_id', 'admission_year']

    def get_queryset(self):
        return get_authorized_students_queryset(self.request.user).select_related(
            'user', 'department', 'program', 'current_semester'
        )


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]
