import datetime
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.accounts.models import Role
from apps.students.models import Department, Program, AcademicYear, Semester, StudentProfile, FacultyAssignment, EnrollmentStatus
from apps.academics.models import Subject, AcademicRecord, AssessmentResult, BacklogRecord
from apps.attendance.models import AttendanceSession, AttendanceRecord, SubjectAttendanceSummary
from apps.lms.models import LMSActivity, LMSAssignmentSubmission, LMSQuizAttempt, LMSEngagementSummary
from apps.engagement.models import Club, ExtracurricularEvent, StudentParticipation, Certification
from apps.placements.models import AptitudeAssessment, CodingAssessment, MockInterview, ResumeReadiness, PlacementCompany, PlacementApplication
from apps.skills.models import SkillCategory, Skill, StudentSkillAssessment
from apps.feedback.models import FeedbackCategory, StudentFeedback, FacultyFeedback
from apps.analytics.models import StudentSuccessSnapshot, AcademicRiskAssessment, PlacementRiskAssessment, RiskIndicator, StudentSegment, ScoreTier, PerformanceTrend, RiskLevel, PlacementReadinessStatus
from apps.interventions.models import InterventionRecommendation, InterventionRecord, InterventionFollowUp, InterventionOutcome

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds database with comprehensive, realistic sample datasets for Smart Campus Analytics"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Starting database seeding for Smart Campus Analytics..."))

        # 1. ACADEMIC CALENDAR & YEARS
        ay_prev, _ = AcademicYear.objects.get_or_create(
            name="2024-2025",
            defaults={"start_date": datetime.date(2024, 8, 1), "end_date": datetime.date(2025, 5, 30), "is_current": False}
        )
        ay_current, _ = AcademicYear.objects.get_or_create(
            name="2025-2026",
            defaults={"start_date": datetime.date(2025, 8, 1), "end_date": datetime.date(2026, 5, 30), "is_current": True}
        )

        semesters = {}
        for num in range(1, 9):
            is_odd = (num % 2 != 0)
            target_ay = ay_prev if num <= 4 else ay_current
            term = "ODD" if is_odd else "EVEN"
            is_curr = (num == 6) # Let Semester 6 be current active semester
            sem, _ = Semester.objects.get_or_create(
                academic_year=target_ay,
                number=num,
                defaults={
                    "term": term,
                    "is_current": is_curr,
                    "start_date": datetime.date(2025, 8, 1) if is_curr else datetime.date(2024, 8, 1),
                    "end_date": datetime.date(2026, 5, 30) if is_curr else datetime.date(2025, 5, 30),
                }
            )
            semesters[num] = sem

        current_sem = semesters[6]
        self.stdout.write(self.style.SUCCESS("[OK] Academic Years and Semesters initialized."))

        # 2. DEPARTMENTS & PROGRAMS
        dept_data = [
            ("CSE", "Computer Science & Engineering", 1995),
            ("IT", "Information Technology", 2000),
            ("ECE", "Electronics & Communication Engineering", 1998),
            ("MECH", "Mechanical Engineering", 1990),
        ]
        departments = {}
        for code, name, year in dept_data:
            dept, _ = Department.objects.get_or_create(
                code=code,
                defaults={"name": name, "established_year": year, "description": f"Department of {name}"}
            )
            departments[code] = dept

        programs = {}
        for code, dept in departments.items():
            prog, _ = Program.objects.get_or_create(
                code=f"BTECH_{code}",
                department=dept,
                defaults={
                    "name": f"B.Tech in {dept.name}",
                    "degree_type": "UG",
                    "total_semesters": 8,
                    "credits_required": 160,
                }
            )
            programs[code] = prog

        self.stdout.write(self.style.SUCCESS("[OK] Departments & Programs created."))

        # 3. CORE USERS (Admin, Faculty, Placement Officer)
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@smartcampus.edu",
                "first_name": "System",
                "last_name": "Administrator",
                "role": Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            }
        )
        admin_user.set_password("admin123")
        admin_user.save()

        faculty_cse, _ = User.objects.get_or_create(
            username="faculty_cse",
            defaults={
                "email": "prof.sharma@smartcampus.edu",
                "first_name": "Rajesh",
                "last_name": "Sharma",
                "role": Role.FACULTY,
                "department": departments["CSE"],
                "designation": "Associate Professor & Head",
                "is_staff": True,
            }
        )
        faculty_cse.set_password("faculty123")
        faculty_cse.save()
        departments["CSE"].head_of_department = faculty_cse
        departments["CSE"].save()

        faculty_ece, _ = User.objects.get_or_create(
            username="faculty_ece",
            defaults={
                "email": "prof.sen@smartcampus.edu",
                "first_name": "Priya",
                "last_name": "Sen",
                "role": Role.FACULTY,
                "department": departments["ECE"],
                "designation": "Professor & Head",
                "is_staff": True,
            }
        )
        faculty_ece.set_password("faculty123")
        faculty_ece.save()
        departments["ECE"].head_of_department = faculty_ece
        departments["ECE"].save()

        placement_head, _ = User.objects.get_or_create(
            username="placement_head",
            defaults={
                "email": "placements@smartcampus.edu",
                "first_name": "Vikram",
                "last_name": "Malhotra",
                "role": Role.PLACEMENT_OFFICER,
                "designation": "Director of Corporate Relations & Placements",
                "is_staff": True,
            }
        )
        placement_head.set_password("placement123")
        placement_head.save()

        self.stdout.write(self.style.SUCCESS("[OK] Institutional administrative and faculty users configured."))

        # 4. SUBJECTS (CSE & ECE Core)
        subjects_data = [
            ("CS601", "Compiler Design", "CSE", 6, 4.0),
            ("CS602", "Machine Learning & Neural Networks", "CSE", 6, 4.0),
            ("CS603", "Cloud Computing & Distributed Systems", "CSE", 6, 3.0),
            ("CS604", "Software Engineering & DevOps", "CSE", 6, 3.0),
            ("CS605", "Computer Networks Lab", "CSE", 6, 2.0),
            ("EC601", "Digital Signal Processing", "ECE", 6, 4.0),
            ("EC602", "VLSI Design & Embedded Systems", "ECE", 6, 4.0),
        ]
        created_subjects = []
        for code, name, dept_code, sem_num, credits_val in subjects_data:
            subj, _ = Subject.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department": departments[dept_code],
                    "semester_number": sem_num,
                    "credits": Decimal(str(credits_val)),
                    "is_elective": False,
                }
            )
            created_subjects.append(subj)

        # Faculty Assignments
        for s in created_subjects:
            f_user = faculty_cse if s.department.code == "CSE" else faculty_ece
            FacultyAssignment.objects.get_or_create(
                faculty=f_user,
                subject=s,
                semester=current_sem,
                section="A",
                academic_year=ay_current
            )

        # 5. SKILL TAXONOMY
        cat_prog, _ = SkillCategory.objects.get_or_create(name="Programming Languages")
        cat_core, _ = SkillCategory.objects.get_or_create(name="Core CS & Systems")
        cat_soft, _ = SkillCategory.objects.get_or_create(name="Soft Skills & Aptitude")

        skill_py, _ = Skill.objects.get_or_create(category=cat_prog, name="Python")
        skill_java, _ = Skill.objects.get_or_create(category=cat_prog, name="Java")
        skill_dsa, _ = Skill.objects.get_or_create(category=cat_core, name="Data Structures & Algorithms")
        skill_db, _ = Skill.objects.get_or_create(category=cat_core, name="Database Design (SQL)")
        skill_comm, _ = Skill.objects.get_or_create(category=cat_soft, name="Verbal Communication")
        skill_prob, _ = Skill.objects.get_or_create(category=cat_soft, name="Problem Solving")

        # 6. PLACEMENT RECRUITING COMPANIES
        companies_data = [
            ("Google India", "Technology & Cloud", Decimal("28.5"), Decimal("8.5"), 0, datetime.date(2026, 7, 10)),
            ("Microsoft", "Enterprise Software", Decimal("26.0"), Decimal("8.0"), 0, datetime.date(2026, 7, 15)),
            ("Amazon Web Services", "Cloud & AI", Decimal("22.0"), Decimal("7.5"), 0, datetime.date(2026, 7, 22)),
            ("TCS Digital", "IT Solutions", Decimal("7.5"), Decimal("6.5"), 1, datetime.date(2026, 8, 5)),
            ("Infosys Specialist Programmer", "Software Engineering", Decimal("9.5"), Decimal("6.8"), 0, datetime.date(2026, 8, 12)),
        ]
        created_companies = []
        for name, ind, pkg, cgpa_req, backlogs_al, d_date in companies_data:
            comp, _ = PlacementCompany.objects.get_or_create(
                name=name,
                defaults={
                    "industry": ind,
                    "package_lpa": pkg,
                    "min_cgpa": cgpa_req,
                    "allowed_backlogs": backlogs_al,
                    "drive_date": d_date,
                }
            )
            created_companies.append(comp)

        # 7. STUDENT SEGMENTS
        seg_high, _ = StudentSegment.objects.get_or_create(
            code="HIGH_FLYERS",
            defaults={
                "name": "High Achievers & Placement Ready",
                "description": "Consistent top-tier GPA, zero backlogs, strong coding profiles.",
                "criteria_summary": "CGPA >= 8.5 AND Attendance >= 85% AND Coding score >= 80",
                "badge_color": "#10B981"
            }
        )
        seg_steady, _ = StudentSegment.objects.get_or_create(
            code="STEADY_PERFORMERS",
            defaults={
                "name": "Consistent Core Achievers",
                "description": "Solid regular performance across curriculum with steady progress.",
                "criteria_summary": "CGPA 7.0 - 8.4 AND Attendance >= 75%",
                "badge_color": "#3B82F6"
            }
        )
        seg_acad_risk, _ = StudentSegment.objects.get_or_create(
            code="ACADEMIC_RISK",
            defaults={
                "name": "Academic Jeopardy & High Risk",
                "description": "Students with severe attendance deficit, active backlogs, or grade collapse.",
                "criteria_summary": "Attendance < 75% OR Active Backlogs > 0 OR CGPA < 6.0",
                "badge_color": "#EF4444"
            }
        )
        seg_place_risk, _ = StudentSegment.objects.get_or_create(
            code="PLACEMENT_GAP",
            defaults={
                "name": "Placement Readiness Deficit",
                "description": "Academically stable students lacking technical coding practice or mock scores.",
                "criteria_summary": "CGPA >= 7.0 AND (Coding score < 50 OR Resume ATS < 50)",
                "badge_color": "#F59E0B"
            }
        )
        seg_disengaged, _ = StudentSegment.objects.get_or_create(
            code="LMS_DISENGAGED",
            defaults={
                "name": "Digital / LMS Disengaged Cohort",
                "description": "Students exhibiting low platform activity and missing deadlines.",
                "criteria_summary": "LMS score < 50 OR Missed assignments >= 3",
                "badge_color": "#8B5CF6"
            }
        )

        # 8. 40 REALISTIC STUDENTS ACROSS DISTINCT ARCHETYPES
        first_names = [
            "Aarav", "Diya", "Rohan", "Ananya", "Ishaan", "Sneha", "Kabir", "Meera",
            "Aditya", "Pooja", "Arjun", "Kavya", "Rahul", "Nisha", "Siddharth", "Tanvi",
            "Vikram", "Shreya", "Aryan", "Rhea", "Manish", "Deepika", "Kunal", "Simran",
            "Varun", "Anika", "Gaurav", "Isha", "Naveen", "Swati", "Prateek", "Sakshi",
            "Abhishek", "Ritu", "Harsh", "Priyanka", "Akash", "Bhavna", "Karthik", "Divya"
        ]
        last_names = [
            "Sharma", "Verma", "Patel", "Reddy", "Iyer", "Nair", "Gupta", "Malhotra",
            "Mehta", "Joshi", "Kulkarni", "Deshmukh", "Chopra", "Rao", "Bhat", "Kapoor",
            "Singhania", "Mukherjee", "Das", "Menon", "Bansal", "Agrawal", "Bhatt", "Pandey",
            "Saxena", "Soni", "Chauhan", "Trivedi", "Mishra", "Dubey", "Gill", "Sandhu",
            "Gowda", "Pillai", "Hegde", "Shetty", "Roy", "Chatterjee", "Basu", "Ghosh"
        ]

        self.stdout.write(self.style.NOTICE("Generating 40 student profiles with multi-semester records..."))

        for i in range(1, 41):
            username = f"student_{i}"
            fname = first_names[i - 1]
            lname = last_names[i - 1]
            dept_choice = departments["CSE"] if i <= 25 else departments["ECE"]
            prog_choice = programs["CSE"] if i <= 25 else programs["ECE"]
            roll_id = f"2023{dept_choice.code}{str(i).zfill(3)}"

            # Archetype determination:
            # 1-10: High Performers
            # 11-20: Steady Performers
            # 21-30: Academic At-Risk
            # 31-35: Placement At-Risk
            # 36-40: LMS Disengaged
            if i <= 10:
                archetype = "HIGH_FLYER"
                cgpa_val = Decimal(str(round(random.uniform(8.70, 9.65), 2)))
                sgpa_val = Decimal(str(round(random.uniform(8.80, 9.80), 2)))
                att_rate = random.randint(90, 98)
                backlog_cnt = 0
                status_choice = EnrollmentStatus.ACTIVE
                risk_lvl = RiskLevel.LOW
                risk_prob = round(random.uniform(0.02, 0.12), 2)
                placement_status = PlacementReadinessStatus.TIER_1_READY
                placement_score_val = Decimal(str(round(random.uniform(85, 96), 1)))
                lms_score_val = Decimal(str(round(random.uniform(88, 98), 1)))
            elif i <= 20:
                archetype = "STEADY"
                cgpa_val = Decimal(str(round(random.uniform(7.20, 8.20), 2)))
                sgpa_val = Decimal(str(round(random.uniform(7.10, 8.30), 2)))
                att_rate = random.randint(78, 88)
                backlog_cnt = 0
                status_choice = EnrollmentStatus.ACTIVE
                risk_lvl = RiskLevel.LOW
                risk_prob = round(random.uniform(0.15, 0.28), 2)
                placement_status = PlacementReadinessStatus.READY
                placement_score_val = Decimal(str(round(random.uniform(70, 82), 1)))
                lms_score_val = Decimal(str(round(random.uniform(72, 85), 1)))
            elif i <= 30:
                archetype = "ACAD_RISK"
                cgpa_val = Decimal(str(round(random.uniform(4.80, 5.80), 2)))
                sgpa_val = Decimal(str(round(random.uniform(4.50, 5.60), 2)))
                att_rate = random.randint(52, 69) # < 75% shortage!
                backlog_cnt = random.randint(1, 3)
                status_choice = EnrollmentStatus.AT_RISK
                risk_lvl = RiskLevel.CRITICAL if att_rate < 60 or backlog_cnt >= 2 else RiskLevel.HIGH
                risk_prob = round(random.uniform(0.72, 0.94), 2)
                placement_status = PlacementReadinessStatus.AT_RISK
                placement_score_val = Decimal(str(round(random.uniform(35, 50), 1)))
                lms_score_val = Decimal(str(round(random.uniform(40, 60), 1)))
            elif i <= 35:
                archetype = "PLACE_RISK"
                cgpa_val = Decimal(str(round(random.uniform(7.40, 8.10), 2)))
                sgpa_val = Decimal(str(round(random.uniform(7.20, 8.00), 2)))
                att_rate = random.randint(80, 90)
                backlog_cnt = 0
                status_choice = EnrollmentStatus.ACTIVE
                risk_lvl = RiskLevel.MEDIUM
                risk_prob = round(random.uniform(0.30, 0.42), 2)
                placement_status = PlacementReadinessStatus.BORDERLINE
                placement_score_val = Decimal(str(round(random.uniform(42, 54), 1))) # Low placement score!
                lms_score_val = Decimal(str(round(random.uniform(70, 82), 1)))
            else:
                archetype = "DISENGAGED"
                cgpa_val = Decimal(str(round(random.uniform(6.10, 6.90), 2)))
                sgpa_val = Decimal(str(round(random.uniform(5.90, 6.70), 2)))
                att_rate = random.randint(74, 80)
                backlog_cnt = 0
                status_choice = EnrollmentStatus.ACTIVE
                risk_lvl = RiskLevel.MEDIUM
                risk_prob = round(random.uniform(0.45, 0.60), 2)
                placement_status = PlacementReadinessStatus.BORDERLINE
                placement_score_val = Decimal(str(round(random.uniform(55, 65), 1)))
                lms_score_val = Decimal(str(round(random.uniform(32, 48), 1))) # Low LMS!

            u, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@student.smartcampus.edu",
                    "first_name": fname,
                    "last_name": lname,
                    "role": Role.STUDENT,
                    "department": dept_choice,
                    "employee_or_student_id": roll_id,
                }
            )
            u.set_password("student123")
            u.save()

            st, _ = StudentProfile.objects.get_or_create(
                user=u,
                defaults={
                    "student_id": roll_id,
                    "department": dept_choice,
                    "program": prog_choice,
                    "current_semester": current_sem,
                    "section": "A",
                    "admission_year": 2023,
                    "expected_graduation_year": 2027,
                    "enrollment_status": status_choice,
                    "mentor": faculty_cse if dept_choice.code == "CSE" else faculty_ece,
                }
            )

            # A. ACADEMIC RECORDS (Semesters 1 through 5)
            for sem_num in range(1, 6):
                hist_sem = semesters[sem_num]
                delta = Decimal(str(round((6 - sem_num) * 0.1, 2)))
                hist_sgpa = min(Decimal("10.0"), max(Decimal("4.0"), sgpa_val - (delta if archetype == 'HIGH_FLYER' else -delta)))
                AcademicRecord.objects.get_or_create(
                    student=st,
                    semester=hist_sem,
                    defaults={
                        "sgpa": hist_sgpa,
                        "cgpa": cgpa_val,
                        "credits_registered": Decimal("24.0"),
                        "credits_earned": Decimal("24.0") if backlog_cnt == 0 else Decimal("20.0"),
                        "backlogs_in_semester": 1 if (backlog_cnt > 0 and sem_num == 5) else 0,
                        "cumulative_backlogs": backlog_cnt if sem_num == 5 else 0,
                        "status": "PASS" if backlog_cnt == 0 or sem_num < 5 else "FAIL",
                    }
                )

            # Backlogs
            if backlog_cnt > 0:
                BacklogRecord.objects.get_or_create(
                    student=st,
                    subject=created_subjects[0],
                    defaults={
                        "semester_failed": semesters[5],
                        "status": "ACTIVE",
                        "attempts_count": 1,
                        "notes": "Failed mid-term and internal evaluation",
                    }
                )

            # B. ATTENDANCE SUMMARIES (Subjects in current semester)
            for subj in created_subjects:
                if subj.department == dept_choice:
                    total_cls = 45
                    attended_cls = int(total_cls * (att_rate / 100.0))
                    SubjectAttendanceSummary.objects.get_or_create(
                        student=st,
                        subject=subj,
                        semester=current_sem,
                        defaults={
                            "total_classes": total_cls,
                            "classes_attended": attended_cls,
                            "attendance_percentage": Decimal(str(round((attended_cls / total_cls) * 100, 2))),
                            "is_shortage": (attended_cls / total_cls) < 0.75,
                        }
                    )

            # C. LMS ENGAGEMENT
            LMSEngagementSummary.objects.get_or_create(
                student=st,
                semester=current_sem,
                defaults={
                    "total_logins": random.randint(45, 110) if archetype != 'DISENGAGED' else random.randint(8, 22),
                    "avg_weekly_logins": Decimal(str(round(random.uniform(4.0, 9.0), 1))) if archetype != 'DISENGAGED' else Decimal("1.5"),
                    "assignments_completed": random.randint(8, 10) if archetype != 'DISENGAGED' else random.randint(3, 5),
                    "assignments_late": random.randint(0, 1) if archetype != 'DISENGAGED' else random.randint(2, 4),
                    "assignments_missed": 0 if archetype != 'DISENGAGED' else random.randint(2, 4),
                    "resources_accessed_count": random.randint(30, 85) if archetype != 'DISENGAGED' else random.randint(6, 14),
                    "lms_engagement_score": lms_score_val,
                }
            )

            # D. SKILL ASSESSMENTS
            StudentSkillAssessment.objects.get_or_create(
                student=st,
                skill=skill_py,
                defaults={
                    "score": Decimal(str(round(random.uniform(80, 98), 1))) if archetype == 'HIGH_FLYER' else Decimal(str(round(random.uniform(45, 75), 1))),
                    "proficiency_level": "ADVANCED" if archetype == 'HIGH_FLYER' else "INTERMEDIATE",
                    "assessment_date": datetime.date(2026, 1, 15),
                }
            )
            StudentSkillAssessment.objects.get_or_create(
                student=st,
                skill=skill_dsa,
                defaults={
                    "score": Decimal(str(round(random.uniform(85, 99), 1))) if archetype == 'HIGH_FLYER' else Decimal(str(round(random.uniform(35, 65), 1))),
                    "proficiency_level": "EXPERT" if archetype == 'HIGH_FLYER' else "BEGINNER",
                    "assessment_date": datetime.date(2026, 1, 20),
                }
            )

            # E. PLACEMENT ASSESSMENTS
            CodingAssessment.objects.get_or_create(
                student=st,
                defaults={
                    "platform": "INTERNAL",
                    "problems_attempted": 20 if archetype == 'HIGH_FLYER' else (4 if archetype == 'PLACE_RISK' else 12),
                    "problems_solved": 19 if archetype == 'HIGH_FLYER' else (1 if archetype == 'PLACE_RISK' else 8),
                    "score": Decimal("95.0") if archetype == 'HIGH_FLYER' else (Decimal("32.0") if archetype == 'PLACE_RISK' else Decimal("72.0")),
                    "assessment_date": datetime.date(2026, 2, 5),
                }
            )
            MockInterview.objects.get_or_create(
                student=st,
                defaults={
                    "interviewer_name": "Industry Panel Lead",
                    "technical_score": Decimal("92.0") if archetype == 'HIGH_FLYER' else (Decimal("40.0") if archetype == 'PLACE_RISK' else Decimal("74.0")),
                    "communication_score": Decimal("88.0") if archetype == 'HIGH_FLYER' else (Decimal("48.0") if archetype == 'PLACE_RISK' else Decimal("76.0")),
                    "behavioral_score": Decimal("90.0") if archetype == 'HIGH_FLYER' else Decimal("65.0"),
                    "overall_score": Decimal("90.0") if archetype == 'HIGH_FLYER' else (Decimal("45.0") if archetype == 'PLACE_RISK' else Decimal("72.0")),
                    "interview_date": datetime.date(2026, 2, 18),
                }
            )
            ResumeReadiness.objects.get_or_create(
                student=st,
                defaults={
                    "ats_score": random.randint(85, 96) if archetype == 'HIGH_FLYER' else (random.randint(35, 48) if archetype == 'PLACE_RISK' else random.randint(65, 78)),
                    "projects_count": 4 if archetype == 'HIGH_FLYER' else 1,
                    "internships_count": 2 if archetype == 'HIGH_FLYER' else 0,
                    "readiness_level": "EXCEPTIONAL" if archetype == 'HIGH_FLYER' else ("NEEDS_WORK" if archetype == 'PLACE_RISK' else "ADEQUATE"),
                }
            )

            # Placement applications for eligible students
            if archetype in ['HIGH_FLYER', 'STEADY']:
                target_comp = created_companies[0] if archetype == 'HIGH_FLYER' else created_companies[3]
                PlacementApplication.objects.get_or_create(
                    student=st,
                    company=target_comp,
                    defaults={
                        "status": "OFFERED" if archetype == 'HIGH_FLYER' else "SHORTLISTED",
                        "package_offered_lpa": target_comp.package_lpa if archetype == 'HIGH_FLYER' else None,
                        "offer_date": datetime.date(2026, 3, 1) if archetype == 'HIGH_FLYER' else None,
                    }
                )

            # F. ANALYTICS SNAPSHOTS & EXPLAINABILITY
            comp_score = Decimal(str(round(float(cgpa_val * 10) * 0.4 + float(att_rate) * 0.25 + float(lms_score_val) * 0.15 + float(placement_score_val) * 0.2, 1)))
            tier = ScoreTier.EXCELLENT if comp_score >= 85 else (ScoreTier.GOOD if comp_score >= 70 else (ScoreTier.AVERAGE if comp_score >= 55 else ScoreTier.AT_RISK))
            
            StudentSuccessSnapshot.objects.get_or_create(
                student=st,
                defaults={
                    "academic_score": Decimal(str(round(float(cgpa_val * 10), 1))),
                    "attendance_score": Decimal(str(att_rate)),
                    "engagement_score": lms_score_val,
                    "placement_score": placement_score_val,
                    "composite_success_score": comp_score,
                    "score_tier": tier,
                    "trend": PerformanceTrend.IMPROVING if archetype == 'HIGH_FLYER' else (PerformanceTrend.DECLINING if archetype == 'ACAD_RISK' else PerformanceTrend.STABLE),
                    "score_breakdown": {
                        "academic_weight": 0.40,
                        "attendance_weight": 0.25,
                        "engagement_weight": 0.15,
                        "placement_weight": 0.20,
                        "archetype": archetype,
                    }
                }
            )

            # Academic Risk Assessment
            AcademicRiskAssessment.objects.get_or_create(
                student=st,
                defaults={
                    "risk_level": risk_lvl,
                    "risk_probability": risk_prob,
                    "predicted_outcome": "High Probability of On-Time Graduation" if risk_lvl == RiskLevel.LOW else ("Severe Risk of Academic Probation & Debarment" if risk_lvl == RiskLevel.CRITICAL else "Academic Watchlist Monitor"),
                    "key_drivers": [
                        {"factor": "Attendance Deficit", "impact": -30} if att_rate < 75 else {"factor": "Consistent Attendance", "impact": 15},
                        {"factor": "Active Backlogs", "impact": -25} if backlog_cnt > 0 else {"factor": "Zero Backlogs", "impact": 20},
                        {"factor": "LMS Platform Inactivity", "impact": -15} if archetype == 'DISENGAGED' else {"factor": "Regular Submissions", "impact": 10},
                    ],
                    "model_version": "v1.0-explainable-ensemble",
                }
            )

            # Placement Risk Assessment
            PlacementRiskAssessment.objects.get_or_create(
                student=st,
                defaults={
                    "readiness_status": placement_status,
                    "readiness_score": placement_score_val,
                    "skill_gaps": ["Dynamic Programming", "System Design"] if archetype == 'PLACE_RISK' else [],
                    "recommended_focus": "Intensive DSA Bootcamp & Resume Overhaul" if archetype == 'PLACE_RISK' else "Tier-1 Technical Interview Prep",
                }
            )

            # Risk Indicators
            if att_rate < 75:
                RiskIndicator.objects.get_or_create(
                    student=st,
                    title="Attendance Deficit (< 75%)",
                    defaults={
                        "category": "ATTENDANCE",
                        "details": f"Aggregate attendance sits at {att_rate}%, failing statutory criteria.",
                        "severity": "CRITICAL" if att_rate < 60 else "WARNING",
                        "is_resolved": False,
                    }
                )

            if backlog_cnt > 0:
                RiskIndicator.objects.get_or_create(
                    student=st,
                    title="Active Course Backlog",
                    defaults={
                        "category": "ACADEMIC",
                        "details": f"Student has {backlog_cnt} uncleared backlog subject(s).",
                        "severity": "CRITICAL",
                        "is_resolved": False,
                    }
                )

            if archetype == 'PLACE_RISK':
                RiskIndicator.objects.get_or_create(
                    student=st,
                    title="Low Coding & Resume Benchmark",
                    defaults={
                        "category": "PLACEMENT",
                        "details": "Resume ATS score below 50% and coding score is deficient for upcoming campus drives.",
                        "severity": "WARNING",
                        "is_resolved": False,
                    }
                )

            # Assign to Segment
            if archetype == 'HIGH_FLYER':
                seg_high.students.add(st)
            elif archetype == 'STEADY':
                seg_steady.students.add(st)
            elif archetype == 'ACAD_RISK':
                seg_acad_risk.students.add(st)
            elif archetype == 'PLACE_RISK':
                seg_place_risk.students.add(st)
            elif archetype == 'DISENGAGED':
                seg_disengaged.students.add(st)

            # Interventions
            if archetype in ['ACAD_RISK', 'PLACE_RISK']:
                rec_title = "Mandatory Attendance Counseling & Remedial Tutoring" if archetype == 'ACAD_RISK' else "Fast-Track Coding Bootcamp & Resume Revamp"
                rec_cat = "ATTENDANCE_COUNSELING" if archetype == 'ACAD_RISK' else "CODING_BOOTCAMP"
                rec, _ = InterventionRecommendation.objects.get_or_create(
                    student=st,
                    title=rec_title,
                    defaults={
                        "description": f"AI identified performance deficit ({archetype}). Immediate faculty intervention recommended.",
                        "category": rec_cat,
                        "priority": "URGENT" if archetype == 'ACAD_RISK' else "HIGH",
                        "status": "APPROVED",
                    }
                )

                inv_rec, _ = InterventionRecord.objects.get_or_create(
                    student=st,
                    recommendation=rec,
                    defaults={
                        "assigned_to": faculty_cse if dept_choice.code == "CSE" else faculty_ece,
                        "intervention_type": "Remedial Coaching & Action Plan",
                        "action_plan": "Bi-weekly progress review meetings, assignment make-up schedule, and mentor check-ins.",
                        "start_date": datetime.date(2026, 2, 1),
                        "target_completion_date": datetime.date(2026, 4, 30),
                        "status": "ACTIVE",
                    }
                )

                InterventionFollowUp.objects.get_or_create(
                    intervention=inv_rec,
                    defaults={
                        "recorded_by": faculty_cse if dept_choice.code == "CSE" else faculty_ece,
                        "follow_up_date": datetime.date(2026, 2, 20),
                        "notes": "Student attended first advisory session. Acknowledged attendance deficit and committed to daily classes.",
                        "impact_assessment": "POSITIVE",
                    }
                )

        self.stdout.write(self.style.SUCCESS("[OK] 40 realistic students seeded with full 360-degree historical datasets!"))
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
