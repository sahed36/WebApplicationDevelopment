from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from .models import Profile, Issue, IssueUpdate

class CampusFixTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="student1", password="StudentPass123!", email="student@example.com")
        self.student.profile.role = Profile.Role.STUDENT
        self.student.profile.save()
        self.staff = User.objects.create_user(username="staff1", password="StaffPass123!", email="staff@example.com")
        self.staff.profile.role = Profile.Role.STAFF
        self.staff.profile.save()
        self.admin = User.objects.create_user(username="admin1", password="AdminPass123!", email="admin@example.com")
        self.admin.profile.role = Profile.Role.ADMIN
        self.admin.profile.save()
        self.issue = Issue.objects.create(title="Wi-Fi broken", description="No signal", category=Issue.Category.INTERNET,
            location="Academic building", student=self.student)
        self.client = Client()

    def test_home_is_public(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_student_dashboard_requires_login(self):
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_student_cannot_open_admin_dashboard(self):
        self.client.login(username="student1", password="StudentPass123!")
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 403)

    def test_student_can_submit_issue(self):
        self.client.login(username="student1", password="StudentPass123!")
        response = self.client.post(reverse("issue_create"), {
            "title": "Broken fan", "description": "Fan is not running",
            "category": Issue.Category.ELECTRICITY, "location": "Room 101", "priority": "NORMAL"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Issue.objects.filter(title="Broken fan", student=self.student).exists())

    def test_student_cannot_view_another_students_issue(self):
        other = User.objects.create_user(username="student2", password="StudentPass123!")
        other.profile.role = Profile.Role.STUDENT
        other.profile.save()
        self.client.login(username="student2", password="StudentPass123!")
        self.assertEqual(self.client.get(reverse("issue_detail", args=[self.issue.pk])).status_code, 403)

    def test_admin_can_assign_issue_to_staff(self):
        self.client.login(username="admin1", password="AdminPass123!")
        response = self.client.post(reverse("assign_issue", args=[self.issue.pk]), {"staff_id": self.staff.pk})
        self.assertEqual(response.status_code, 302)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.assigned_staff, self.staff)
