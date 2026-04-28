from django.contrib import admin
from .models import UserProfile, Department, Audit, Finding, AuditReport


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department']
    list_filter = ['role']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_user', 'created_at']
    search_fields = ['name']


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'status', 'start_date', 'end_date', 'assigned_auditor']
    list_filter = ['status', 'department']
    search_fields = ['title']
    date_hierarchy = 'start_date'


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ['title', 'audit', 'severity', 'status', 'target_closure_date', 'is_overdue']
    list_filter = ['severity', 'status']
    search_fields = ['title']
    readonly_fields = ['closed_at']


@admin.register(AuditReport)
class AuditReportAdmin(admin.ModelAdmin):
    list_display = ['audit', 'generated_by', 'generated_at']
    readonly_fields = ['generated_at']
