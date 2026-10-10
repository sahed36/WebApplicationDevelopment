from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .decorators import role_required
from .forms import StudentRegistrationForm, IssueForm
from .models import Issue, IssueUpdate, Profile

def home(request):
    return render(request, "issues/home.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.save(update_fields=["email"])
            login(request, user)
            messages.success(request, "Your student account has been created.")
            return redirect("student_dashboard")
    else:
        form = StudentRegistrationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    role = request.user.profile.role
    if role == Profile.Role.ADMIN:
        return redirect("admin_dashboard")
    if role == Profile.Role.STAFF:
        return redirect("staff_dashboard")
    return redirect("student_dashboard")

@role_required(Profile.Role.STUDENT)
def student_dashboard(request):
    issues = Issue.objects.filter(student=request.user).select_related("student", "assigned_staff")
    context = {
        "issues": issues,
        "total_count": issues.count(),
        "pending_count": issues.filter(status=Issue.Status.PENDING).count(),
        "resolved_count": issues.filter(status=Issue.Status.RESOLVED).count(),
    }
    return render(request, "issues/student_dashboard.html", context)

@role_required(Profile.Role.STUDENT)
def issue_create(request):
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.student = request.user
            issue.save()
            IssueUpdate.objects.create(issue=issue, updated_by=request.user, old_status="", new_status=issue.status, note="Report submitted.")
            messages.success(request, f"Report CF-{issue.pk} was submitted.")
            return redirect("student_dashboard")
    else:
        form = IssueForm()
    return render(request, "issues/issue_form.html", {"form": form})

@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue.objects.select_related("student", "assigned_staff"), pk=pk)
    role = request.user.profile.role
    if role == Profile.Role.STUDENT and issue.student_id != request.user.id:
        raise PermissionDenied("You can only view reports you submitted.")
    if role == Profile.Role.STAFF and issue.assigned_staff_id != request.user.id:
        raise PermissionDenied("You can only view reports assigned to you.")
    return render(request, "issues/issue_detail.html", {"issue": issue, "history": issue.updates.select_related("updated_by")})

@role_required(Profile.Role.ADMIN)
def admin_dashboard(request):
    query = request.GET.get("q", "").strip()
    issues = Issue.objects.select_related("student", "assigned_staff")
    if query:
        issues = issues.filter(Q(title__icontains=query) | Q(location__icontains=query) | Q(description__icontains=query))
    counts = {status: Issue.objects.filter(status=status).count() for status, _ in Issue.Status.choices}
    staff = User.objects.filter(profile__role=Profile.Role.STAFF).order_by("first_name", "username")
    return render(request, "issues/admin_dashboard.html", {"issues": issues, "staff": staff, "counts": counts, "query": query})

@role_required(Profile.Role.ADMIN)
@require_POST
def assign_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    staff = get_object_or_404(User, pk=request.POST.get("staff_id"), profile__role=Profile.Role.STAFF)
    issue.assigned_staff = staff
    issue.save(update_fields=["assigned_staff", "updated_at"])
    IssueUpdate.objects.create(issue=issue, updated_by=request.user, old_status=issue.status, new_status=issue.status, note=f"Assigned to {staff.get_full_name() or staff.username}.")
    messages.success(request, f"CF-{issue.pk} assigned to {staff.get_full_name() or staff.username}.")
    return redirect("admin_dashboard")

@role_required(Profile.Role.ADMIN)
@require_POST
def change_user_role(request, pk):
    user = get_object_or_404(User, pk=pk)
    role = request.POST.get("role", "")
    if role not in Profile.Role.values:
        messages.error(request, "Choose a valid role.")
    elif user.pk == request.user.pk and role != Profile.Role.ADMIN:
        messages.error(request, "You cannot remove your own administrator role here.")
    else:
        user.profile.role = role
        user.profile.save(update_fields=["role"])
        messages.success(request, f"Role updated for {user.username}.")
    return redirect("manage_users")

@role_required(Profile.Role.ADMIN)
def manage_users(request):
    users = User.objects.select_related("profile").order_by("username")
    return render(request, "issues/manage_users.html", {"users": users, "roles": Profile.Role.choices})

def _change_status(issue, actor, new_status, note):
    old_status = issue.status
    issue.status = new_status
    if note.strip():
        issue.resolution_note = note.strip()
    issue.save()
    IssueUpdate.objects.create(issue=issue, updated_by=actor, old_status=old_status, new_status=new_status, note=note.strip() or "Status updated.")

@role_required(Profile.Role.STAFF, Profile.Role.ADMIN)
@require_POST
def update_issue_status(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    role = request.user.profile.role
    if role == Profile.Role.STAFF and issue.assigned_staff_id != request.user.id:
        raise PermissionDenied("You can only update reports assigned to you.")
    new_status = request.POST.get("status", "")
    valid_statuses = [value for value, _ in Issue.Status.choices]
    if new_status not in valid_statuses:
        messages.error(request, "Choose a valid status.")
    else:
        _change_status(issue, request.user, new_status, request.POST.get("note", ""))
        messages.success(request, f"CF-{issue.pk} status updated.")
    return redirect("issue_detail", pk=issue.pk)

@role_required(Profile.Role.STAFF)
def staff_dashboard(request):
    issues = Issue.objects.filter(assigned_staff=request.user).select_related("student", "assigned_staff")
    return render(request, "issues/staff_dashboard.html", {"issues": issues})
