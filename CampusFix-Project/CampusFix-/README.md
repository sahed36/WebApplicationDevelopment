# CampusFix — University Problem Reporting and Resolution System

CampusFix is a multi-page Django web application for reporting and tracking campus maintenance issues. Students submit issues, administrators assign staff and monitor progress, and maintenance staff update status with resolution notes.

## Features
- Public landing page and student registration/login
- Role-based access: `STUDENT`, `STAFF`, `ADMIN`
- Django authentication and CSRF protection
- Issue reporting with category, campus location and priority
- Admin assignment, user role management, search and status analytics
- Staff dashboard for assigned issues
- Activity history and resolution notes
- Responsive Bootstrap 5 interface and Chart.js dashboard

## Stack
Python 3.11+, Django 5.1–5.2, MySQL 8+, Bootstrap 5, Chart.js, Gunicorn and WhiteNoise.

## 1. Setup locally
Create and activate a virtual environment.

Windows PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The default configuration uses SQLite for the fastest first run. This is useful for checking the UI before connecting MySQL. To use MySQL as required for the final lab, create a database and user:
```sql
CREATE DATABASE campusfix CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'campusfix_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON campusfix.* TO 'campusfix_user'@'localhost';
FLUSH PRIVILEGES;
```
Copy `.env.example` to `.env` and export the values into your environment, or set the variables in your terminal. Django does not automatically load `.env` in this template, so install `python-dotenv` and run `python -c "from dotenv import load_dotenv; load_dotenv()"` is not persistent between commands. The simplest approach is to set environment variables in your terminal or add `from dotenv import load_dotenv; load_dotenv(BASE_DIR / '.env')` immediately after defining `BASE_DIR` in `campusfix/settings.py`.

Set `DB_ENGINE=mysql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`. On Windows, `mysqlclient` installation may require a compatible wheel/build tools; if it fails, use a supported Python version and follow mysqlclient's official installation notes.

Then run:
```bash
python manage.py makemigrations issues
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open `http://127.0.0.1:8000/`.

## 2. Configure roles
Public registration creates student accounts only. Create a staff/admin user with `python manage.py createsuperuser`, log in to `/django-admin/`, open Profiles, and set the user's role to `STAFF` or `ADMIN`. A Django superuser bypasses Django model-admin permissions but the CampusFix dashboard role is controlled by the Profile role, so set it explicitly to `ADMIN` for dashboard access.

## 3. Main routes
- `/` — home page
- `/register/`, `/login/`, `/logout/`
- `/student/` — student reports
- `/issues/new/` — create report
- `/issues/<id>/` — report detail and history
- `/staff/` — assigned staff reports
- `/admin-panel/` — admin dashboard and assignment
- `/admin-panel/users/` — role management
- `/django-admin/` — Django admin site

## 4. Run tests
```bash
python manage.py test
python manage.py check
```
Tests cover public homepage access, login requirement, role restrictions, report creation, ownership restrictions and admin assignment.

## 5. GitHub
Create an empty repository on GitHub, then:
```bash
git init
git add .
git commit -m "Build CampusFix Django application"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/campusfix-django.git
git push -u origin main
```
Replace the placeholder username with your own GitHub username.

## 6. Deployment overview
Deploy to a Python-compatible host that supports Django and connects to MySQL. Configure environment variables in the host dashboard:
- `DJANGO_SECRET_KEY` (strong random value)
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=your-real-hostname`
- `DB_ENGINE=mysql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

Build command:
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```
Start command:
```bash
gunicorn campusfix.wsgi:application
```
Ensure the provider supports persistent MySQL connectivity. Free tiers and database availability change; confirm current provider limits. For production, use HTTPS, a strong secret, backups, a restricted database user, and review Django's deployment checklist:
`python manage.py check --deploy`.

## Security and scope notes
- This is an educational prototype, not a fully audited production service.
- Public signup only grants the Student role; administrators control role changes.
- Do not expose `/django-admin/` credentials or commit `.env`.
- Set `DEBUG=False` and configure real allowed hosts before deployment.
- No file uploads, email/SMS notifications, comments or real-time updates are included in this version.
- Review the Django deployment checklist and hosting provider's current instructions before publishing.

## Suggested demo workflow
1. Register a student and submit a Wi-Fi or classroom maintenance report.
2. Log in as admin and assign the issue to a staff user.
3. Log in as that staff user, update status to In progress and then Resolved, and add a note.
4. Log in as student to show the report status and history.
5. Show the admin status chart, search, user-role controls, tests and GitHub README.
