from django.contrib import admin
from .models import Profile, Issue, IssueUpdate
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at")
    list_filter = ("role",)
@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "location", "status", "priority", "student", "assigned_staff", "created_at")
    list_filter = ("status", "category", "priority")
    search_fields = ("title", "description", "location", "student__username")
@admin.register(IssueUpdate)
class IssueUpdateAdmin(admin.ModelAdmin):
    list_display = ("issue", "updated_by", "old_status", "new_status", "created_at")
