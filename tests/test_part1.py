import pytest
from decimal import Decimal
import datetime
from django.urls import reverse
from django.test import Client, TestCase
from django.core.exceptions import ValidationError
from apps.accounts.models import User, Role
from apps.students.models import Department, Program, AcademicYear, Semester, StudentProfile
from apps.attendance.models import SubjectAttendanceSummary
from apps.academics.models import Subject

class StudentAnalyticsPlatformTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Departments
        self.dept_cse = Department.objects.create(code="CSE", name="Computer Science", established_year=2000)
        self.dept_ece = Department.objects.create(code="ECE", name="Electronics", established_year=2001)

        # Programs
        self.prog_cse = Program.objects.create(code="BTECH_CSE", name="BTech CSE", department=self.dept_cse)
        self.prog_ece = Program.objects.create(code="BTECH_ECE", name="BTech ECE", department=self.dept_ece)

        # Academic Year & Semester
        self.ay = AcademicYear.objects.create(
            name="2025-2026",
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 5, 30),
            is_current=True
        )
        self.sem6 = Semester.objects.create(
            academic_year=self.ay,
            number=6,
            term="EVEN",
            is_current=True,
            start_date=datetime.date(2025, 8, 1),
            end_date=datetime.date(2026, 5, 30)
        )

        # Subject
        self.subject = Subject.objects.create(
            code="CS601",
            name="Compiler Design",
            department=self.dept_cse,
            semester_number=6,
            credits=Decimal("4.0")
        )

        # 1. Admin User
        self.admin_user = User.objects.create_user(
            username="test_admin", password="password123", role=Role.ADMIN, is_staff=True, is_superuser=True
        )

        # 2. Faculty User (CSE)
        self.faculty_cse = User.objects.create_user(
            username="faculty_cse", password="password123", role=Role.FACULTY, department=self.dept_cse
        )

        # 3. Faculty User (ECE)
        self.faculty_ece = User.objects.create_user(
            username="faculty_ece", password="password123", role=Role.FACULTY, department=self.dept_ece
        )

        # 4. Student 1 (CSE)
        self.user_s1 = User.objects.create_user(username="stu_1", password="password123", role=Role.STUDENT)
        self.student_1 = StudentProfile.objects.create(
            user=self.user_s1,
            student_id="2023CSE001",
            department=self.dept_cse,
            program=self.prog_cse,
            current_semester=self.sem6,
            admission_year=2023,
            expected_graduation_year=2027
        )

        # 5. Student 2 (CSE)
        self.user_s2 = User.objects.create_user(username="stu_2", password="password123", role=Role.STUDENT)
        self.student_2 = StudentProfile.objects.create(
            user=self.user_s2,
            student_id="2023CSE002",
            department=self.dept_cse,
            program=self.prog_cse,
            current_semester=self.sem6,
            admission_year=2023,
            expected_graduation_year=2027
        )

    def test_user_roles(self):
        """Test custom User model role helper methods."""
        self.assertTrue(self.admin_user.is_admin_role)
        self.assertTrue(self.faculty_cse.is_faculty_role)
        self.assertTrue(self.user_s1.is_student_role)
        self.assertFalse(self.user_s1.is_faculty_role)

    def test_student_cross_tenant_isolation_forbidden(self):
        """CRITICAL SECURITY TEST: Student 1 CANNOT view Student 2's private profile."""
        self.client.login(username="stu_1", password="password123")
        
        # Try accessing student 2's detail view
        url = reverse("students:student_detail", kwargs={"student_id": self.student_2.student_id})
        response = self.client.get(url)
        
        # Must return 403 Forbidden!
        self.assertEqual(response.status_code, 403)

    def test_student_self_access_allowed(self):
        """Student 1 CAN view their own profile."""
        self.client.login(username="stu_1", password="password123")
        url = reverse("students:student_detail", kwargs={"student_id": self.student_1.student_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student_1.student_id)

    def test_admin_can_access_any_student(self):
        """Admin has permission to view all student profiles."""
        self.client.login(username="test_admin", password="password123")
        url = reverse("students:student_detail", kwargs={"student_id": self.student_1.student_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_attendance_impossible_values_validation(self):
        """Test that attended classes exceeding conducted classes raises ValidationError."""
        summary = SubjectAttendanceSummary(
            student=self.student_1,
            subject=self.subject,
            semester=self.sem6,
            total_classes=40,
            classes_attended=45  # Impossible!
        )
        with self.assertRaises(ValidationError):
            summary.clean()

    def test_attendance_shortage_calculation(self):
        """Test automatic calculation of attendance percentage and shortage flag."""
        summary = SubjectAttendanceSummary.objects.create(
            student=self.student_1,
            subject=self.subject,
            semester=self.sem6,
            total_classes=50,
            classes_attended=30  # 60% < 75%
        )
        self.assertEqual(summary.attendance_percentage, Decimal("60.00"))
        self.assertTrue(summary.is_shortage)

    def test_drf_api_student_scoping(self):
        """Test DRF API data scoping: Student only sees themselves."""
        self.client.login(username="stu_1", password="password123")
        response = self.client.get("/api/students/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get("results", data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["student_id"], self.student_1.student_id)
