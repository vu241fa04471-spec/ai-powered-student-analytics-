# Smart Campus Analytics — AI-Powered Student Success Platform

A comprehensive, production-minded higher-education analytics platform built on **Python 3.11/3.12**, **Django 5.1 LTS**, and **Django REST Framework**.

---

## 🏛️ System Architecture

```
smart_campus_analytics/
├── manage.py                   # Django management entry point
├── requirements.txt            # Dependency specifications
├── .env.example / .env         # Environment configuration
├── config/                     # Project configuration
│   ├── settings.py             # Modular settings & database routing
│   ├── urls.py                 # Core routing & REST API router
│   ├── wsgi.py / asgi.py
├── apps/                       # 11 Domain-Driven Applications
│   ├── accounts/               # Custom User, 4 Roles, Server-side RBAC & Access scoping
│   ├── students/               # Departments, Programs, Academic Years, Semesters, 360° Profiles
│   ├── academics/              # Subjects, Grades, SGPA/CGPA, Mid/End-Sem Exams, Backlogs
│   ├── attendance/             # Lecture sessions, attendance logs, statutory <75% shortages
│   ├── lms/                    # Digital activity, assignments timeliness, quizzes, LMS index
│   ├── engagement/             # Clubs, Hackathons, Workshops, Certifications, Leadership
│   ├── placements/             # Coding tests, Aptitude, Mock interviews, Resume ATS, Drives
│   ├── skills/                 # Skill taxonomy, technical & soft skill assessments
│   ├── feedback/               # Student course feedback, Confidential faculty mentoring notes
│   ├── analytics/              # Multi-factor Success Scores, Explainable Risk Engine, Cohorts
│   └── interventions/          # Remedial tutoring, attendance counseling, follow-up logs
├── templates/                  # Modern UI with Bootstrap 5, dark/light accents, micro-animations
├── static/                     # Design system CSS and JS
└── tests/                      # Automated security, isolation, and validation test suite
```

---

## 👥 User Roles & Server-Side Security Isolation

The system enforces strict server-side authorization. A student **can never access another student's private records** simply by altering a URL parameter or API ID:

1. **Administrator (`ADMIN`)**
   - Institution-wide KPI monitoring, department analytics, user administration, data management.
2. **Faculty (`FACULTY`)**
   - Department-scoped roster, mentored students, attendance shortage watchlist, intervention action plans.
3. **Placement Officer (`PLACEMENT_OFFICER`)**
   - Campus drive readiness, Tier-1 company matching, coding & mock interview gap analysis.
4. **Student (`STUDENT`)**
   - Strict self-service view: personal CGPA trajectory, attendance %, LMS engagement, AI Success Score & recommendations.

---

## ⚡ Quick Start & Setup

### 1. Environment & Dependencies
```bash
# Clone or navigate to the repository
cd student_data

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (already satisfied in venv)
pip install -r requirements.txt
```

### 2. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed Realistic Sample Datasets
Populates departments, academic years, courses, 40+ multi-semester students across 5 archetypes (High Flyers, Steady, Academic Risk, Placement Gap, Disengaged), and baseline analytics:
```bash
python manage.py seed_data
```

### 4. Run Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Demo Login Credentials (Ready to Test)

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full institutional access & admin portal |
| **Faculty (CSE)** | `faculty_cse` | `faculty123` | Computer Science department & mentees |
| **Faculty (ECE)** | `faculty_ece` | `faculty123` | Electronics department & mentees |
| **Placement Head** | `placement_head` | `placement123` | Placement readiness & campus hiring drives |
| **Student (High Flyer)** | `student_1` | `student123` | Personal profile (CGPA: 9.35, 96% attendance) |
| **Student (At-Risk)** | `student_21` | `student123` | Personal profile (CGPA: 5.20, 58% attendance, backlogs) |
| **Student (Placement Gap)** | `student_31` | `student123` | Personal profile (CGPA: 7.80, low coding scores) |

---

## 🧪 Automated Testing
Run the automated test suite verifying tenant isolation, role permissions, and attendance validation:
```bash
python manage.py test tests
```
