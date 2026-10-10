from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Issue

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Full name")
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["title", "description", "category", "location", "priority"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Wi-Fi not working in Room 204"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Describe what happened and when you noticed it."}),
            "location": forms.TextInput(attrs={"placeholder": "Building, floor, room or campus area"}),
        }
