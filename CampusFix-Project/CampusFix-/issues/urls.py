from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("issues/new/", views.issue_create, name="issue_create"),
    path("issues/<int:pk>/", views.issue_detail, name="issue_detail"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/issues/<int:pk>/assign/", views.assign_issue, name="assign_issue"),
    path("admin-panel/users/", views.manage_users, name="manage_users"),
    path("admin-panel/users/<int:pk>/role/", views.change_user_role, name="change_user_role"),
    path("issues/<int:pk>/status/", views.update_issue_status, name="update_issue_status"),
]
