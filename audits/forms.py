from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Audit, Finding, AuditReport


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
        })
    )


class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['title', 'department', 'assigned_auditor', 'start_date', 'end_date',
                  'status', 'objectives', 'scope']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'assigned_auditor': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'scope': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class FindingForm(forms.ModelForm):
    class Meta:
        model = Finding
        fields = ['title', 'description', 'severity', 'recommendation',
                  'target_closure_date', 'status', 'response_notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'recommendation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'target_closure_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'response_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FindingResponseForm(forms.ModelForm):
    class Meta:
        model = Finding
        fields = ['response_notes', 'status']
        widgets = {
            'response_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                    'placeholder': 'Enter your response / action taken...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ReportNotesForm(forms.ModelForm):
    class Meta:
        model = AuditReport
        fields = ['summary_notes']
        widgets = {
            'summary_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                                                   'placeholder': 'Enter executive summary notes...'}),
        }


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
