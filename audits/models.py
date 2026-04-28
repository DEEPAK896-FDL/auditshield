import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('audit_manager', 'Audit Manager'),
        ('auditee_head', 'Auditee Head'),
        ('observer', 'Observer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, blank=True, default='')
    department = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

    @property
    def avatar_initials(self):
        first = self.user.first_name[:1] if self.user.first_name else ''
        last = self.user.last_name[:1] if self.user.last_name else ''
        if first or last:
            return (first + last).upper()
        return self.user.username[:2].upper()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    head_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='headed_departments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Audit(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('closed', 'Closed'),
    ]
    title = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='audits')
    assigned_auditor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_audits'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_audits'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    objectives = models.TextField(blank=True)
    scope = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return self.end_date < datetime.date.today() and self.status != 'closed'

    @property
    def findings_count(self):
        return self.findings.count()

    @property
    def open_findings_count(self):
        return self.findings.filter(status='open').count()

    @property
    def critical_findings_count(self):
        return self.findings.filter(severity='critical').count()


class Finding(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='findings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    recommendation = models.TextField()
    target_closure_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    response_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.audit.title})"

    @property
    def is_overdue(self):
        return self.target_closure_date < datetime.date.today() and self.status != 'closed'

    @property
    def severity_color(self):
        colors = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'secondary',
        }
        return colors.get(self.severity, 'secondary')


class AuditReport(models.Model):
    audit = models.OneToOneField(Audit, on_delete=models.CASCADE, related_name='report')
    generated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_reports'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    summary_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Audit Report'

    def __str__(self):
        return f"Report — {self.audit.title}"
