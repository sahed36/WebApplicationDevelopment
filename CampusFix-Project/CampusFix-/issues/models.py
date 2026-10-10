from django.conf import settings
from django.db import models
from django.utils import timezone

class Profile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        STAFF = "STAFF", "Maintenance staff"
        ADMIN = "ADMIN", "Administrator"
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Issue(models.Model):
    class Category(models.TextChoices):
        ELECTRICITY = "ELECTRICITY", "Electricity"
        CLEANLINESS = "CLEANLINESS", "Cleanliness"
        FURNITURE = "FURNITURE", "Furniture"
        INTERNET = "INTERNET", "Internet / Wi-Fi"
        WATER = "WATER", "Water supply"
        CLASSROOM = "CLASSROOM", "Classroom equipment"
        OTHER = "OTHER", "Other"
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        RESOLVED = "RESOLVED", "Resolved"
        REJECTED = "REJECTED", "Rejected"
    class Priority(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "High"

    title = models.CharField(max_length=120)
    description = models.TextField(max_length=3000)
    category = models.CharField(max_length=20, choices=Category.choices)
    location = models.CharField(max_length=160)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reported_issues")
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues")
    resolution_note = models.TextField(max_length=1500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"CF-{self.pk}: {self.title}"

class IssueUpdate(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="updates")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="issue_updates")
    old_status = models.CharField(max_length=15, choices=Issue.Status.choices, blank=True)
    new_status = models.CharField(max_length=15, choices=Issue.Status.choices, blank=True)
    note = models.CharField(max_length=1500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"Update for CF-{self.issue_id} at {self.created_at:%Y-%m-%d %H:%M}"
