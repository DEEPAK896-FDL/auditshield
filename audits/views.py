import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q

from .models import Audit, Finding, Department, AuditReport
from .forms import AuditForm, FindingForm, FindingResponseForm, LoginForm, ReportNotesForm, ProfileEditForm
from .decorators import (
    manager_required,
    auditee_required,
    manager_or_auditee_required,
    read_access_required,
)
from .utils import generate_audit_pdf


# ── Authentication ────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # automatically updates last_login
            return redirect('dashboard')  # All roles go to dashboard
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'audits/login.html', {})


@never_cache
def logout_view(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    # Redirect to landing page — NOT login page
    response = redirect('landing')
    # Set headers to prevent browser caching authenticated pages
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ── Dashboard ─────────────────────────────────────────────────────────────────

@never_cache
@login_required
@read_access_required
def dashboard(request):
    try:
        role = request.user.profile.role
    except Exception:
        return redirect('login')

    if role in ('audit_manager', 'observer'):
        # Observer sees the same full dashboard as manager (read-only)
        all_findings = Finding.objects.all()
        overdue_findings = [f for f in all_findings if f.is_overdue]

        # ── Chart data: raw Python values inlined into template ──────────
        ctx_planned  = Audit.objects.filter(status='planned').count()
        ctx_ongoing  = Audit.objects.filter(status='ongoing').count()
        ctx_closed   = Audit.objects.filter(status='closed').count()

        ctx_critical = Finding.objects.filter(severity='critical').count()
        ctx_high     = Finding.objects.filter(severity='high').count()
        ctx_medium   = Finding.objects.filter(severity='medium').count()
        ctx_low      = Finding.objects.filter(severity='low').count()

        dept_qs = (
            Audit.objects
            .values('department__name')
            .annotate(total=Count('id'))
            .order_by('department__name')
        )
        ctx_dept_labels = [d['department__name'] or 'Unknown' for d in dept_qs]
        ctx_dept_values = [d['total'] for d in dept_qs]

        context = {
            'total_audits': Audit.objects.count(),
            'planned_audits': ctx_planned,
            'ongoing_audits': ctx_ongoing,
            'closed_audits':  ctx_closed,
            'open_findings': all_findings.filter(status='open').count(),
            'critical_findings': all_findings.filter(severity='critical').count(),
            'overdue_findings': overdue_findings[:5],
            'overdue_count': len(overdue_findings),
            'recent_audits': Audit.objects.order_by('-created_at')[:5],
            'ctx_planned':     ctx_planned,
            'ctx_ongoing':     ctx_ongoing,
            'ctx_closed':      ctx_closed,
            'ctx_critical':    ctx_critical,
            'ctx_high':        ctx_high,
            'ctx_medium':      ctx_medium,
            'ctx_low':         ctx_low,
            'ctx_dept_labels': ctx_dept_labels,
            'ctx_dept_values': ctx_dept_values,
        }
    elif role == 'auditee_head':
        # Auditee Head
        try:
            dept_name = request.user.profile.department
        except Exception:
            dept_name = ''

        my_audits = Audit.objects.filter(department__name=dept_name) if dept_name else Audit.objects.none()
        finding_ids = Finding.objects.filter(audit__in=my_audits)
        overdue_findings = [f for f in finding_ids if f.is_overdue]

        context = {
            'my_audits': my_audits,
            'open_findings_count': finding_ids.filter(status='open').count(),
            'in_progress_count': finding_ids.filter(status='in_progress').count(),
            'overdue_findings': overdue_findings,
            'overdue_count': len(overdue_findings),
        }
    else:
        return redirect('access_denied')

    return render(request, 'audits/dashboard.html', context)


# ── Audit CRUD ────────────────────────────────────────────────────────────────

@never_cache
@login_required
@read_access_required
def audit_list(request):
    try:
        role = request.user.profile.role
        dept_name = request.user.profile.department
    except Exception:
        role = 'auditee_head'
        dept_name = ''

    if role in ('audit_manager', 'observer'):
        audits = Audit.objects.all().select_related('department', 'assigned_auditor')
    else:
        audits = Audit.objects.filter(department__name=dept_name).select_related('department', 'assigned_auditor')

    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')

    if status_filter:
        audits = audits.filter(status=status_filter)
    if q:
        audits = audits.filter(title__icontains=q)

    paginator = Paginator(audits, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'q': q,
    }
    return render(request, 'audits/audit_list.html', context)


@login_required
@manager_required
def audit_create(request):
    form = AuditForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        audit = form.save(commit=False)
        audit.created_by = request.user
        audit.save()
        messages.success(request, f'Audit "{audit.title}" created successfully.')
        return redirect('audit_detail', pk=audit.pk)
    return render(request, 'audits/audit_create.html', {'form': form})


@never_cache
@login_required
@read_access_required
def audit_detail(request, pk):
    audit = get_object_or_404(Audit, pk=pk)

    # Auditees can only view their own department's audits
    try:
        profile = request.user.profile
        if profile.role == 'auditee_head':
            if audit.department.name != profile.department:
                messages.error(request, 'You can only view audits for your department.')
                return redirect('audit_list')
    except Exception:
        pass

    findings = audit.findings.all()
    severity_summary = {
        'critical': findings.filter(severity='critical').count(),
        'high': findings.filter(severity='high').count(),
        'medium': findings.filter(severity='medium').count(),
        'low': findings.filter(severity='low').count(),
    }
    context = {
        'audit': audit,
        'findings': findings,
        'severity_summary': severity_summary,
    }
    return render(request, 'audits/audit_detail.html', context)


@login_required
@manager_required
def audit_edit(request, pk):
    audit = get_object_or_404(Audit, pk=pk)
    form = AuditForm(request.POST or None, instance=audit)
    if request.method == 'POST' and form.is_valid():
        updated = form.save()
        if updated.status == 'closed':
            AuditReport.objects.get_or_create(
                audit=updated,
                defaults={'generated_by': request.user}
            )
        messages.success(request, f'Audit "{updated.title}" updated successfully.')
        return redirect('audit_detail', pk=updated.pk)
    return render(request, 'audits/audit_edit.html', {'form': form, 'audit': audit})


# ── Finding CRUD ──────────────────────────────────────────────────────────────

@login_required
@manager_required
def finding_create(request, pk):
    audit = get_object_or_404(Audit, pk=pk)
    form = FindingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        finding = form.save(commit=False)
        finding.audit = audit
        finding.save()
        messages.success(request, f'Finding "{finding.title}" added successfully.')
        return redirect('audit_detail', pk=audit.pk)
    return render(request, 'audits/finding_create.html', {'form': form, 'audit': audit})


@never_cache
@login_required
@read_access_required
def finding_detail(request, pk):
    finding = get_object_or_404(Finding, pk=pk)

    # Auditees can only view findings in their department
    try:
        profile = request.user.profile
        if profile.role == 'auditee_head':
            if finding.audit.department.name != profile.department:
                messages.error(request, 'You can only view findings for your department.')
                return redirect('audit_list')
    except Exception:
        pass

    try:
        role = request.user.profile.role
    except Exception:
        role = 'auditee_head'

    response_form = None
    if role == 'auditee_head':
        response_form = FindingResponseForm(instance=finding)

    context = {
        'finding': finding,
        'response_form': response_form,
    }
    return render(request, 'audits/finding_detail.html', context)


@login_required
@manager_or_auditee_required
def finding_edit(request, pk):
    finding = get_object_or_404(Finding, pk=pk)
    try:
        role = request.user.profile.role
    except Exception:
        role = 'auditee_head'

    if role == 'audit_manager':
        form_class = FindingForm
    else:
        form_class = FindingResponseForm

    form = form_class(request.POST or None, instance=finding)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Finding updated successfully.')
        return redirect('finding_detail', pk=finding.pk)

    return render(request, 'audits/finding_edit.html', {
        'form': form,
        'finding': finding,
    })


@login_required
def finding_close(request, pk):
    finding = get_object_or_404(Finding, pk=pk)
    if request.method == 'POST':
        finding.status = 'closed'
        finding.closed_at = timezone.now()
        finding.save()
        messages.success(request, f'Finding "{finding.title}" marked as closed.')
    return redirect('audit_detail', pk=finding.audit.pk)


# ── Finding List (All Findings) ───────────────────────────────────────────────

@never_cache
@login_required
@read_access_required
def finding_list(request):
    try:
        role = request.user.profile.role
    except Exception:
        role = 'auditee_head'
    if role in ('audit_manager', 'observer'):
        findings = Finding.objects.select_related(
            'audit', 'audit__department'
        ).order_by('-created_at')
    else:
        try:
            dept = request.user.profile.department
        except Exception:
            dept = ''
        findings = Finding.objects.filter(
            audit__department__name=dept
        ).select_related('audit', 'audit__department').order_by('-created_at')

    status_filter = request.GET.get('status', '')
    if status_filter:
        findings = findings.filter(status=status_filter)

    today = date.today()
    findings = list(findings)
    for f in findings:
        f.overdue = (f.target_closure_date < today and f.status != 'closed')

    context = {
        'findings': findings,
        'status_filter': status_filter,
        'page_title': 'All Findings',
    }
    return render(request, 'audits/finding_list.html', context)


# ── Department Analytics ──────────────────────────────────────────────────────

@never_cache
@login_required
@read_access_required
def department_analytics(request):
    departments = Department.objects.all()
    dept_data = []
    for dept in departments:
        dept_audits = dept.audits.all()
        dept_findings = Finding.objects.filter(audit__in=dept_audits)
        overdue = sum(1 for f in dept_findings if f.is_overdue)
        dept_data.append({
            'dept': dept,
            'total_audits': dept_audits.count(),
            'open_findings': dept_findings.filter(status='open').count(),
            'overdue_findings': overdue,
            'closed_audits': dept_audits.filter(status='closed').count(),
        })
    return render(request, 'audits/department_analytics.html', {'dept_data': dept_data})


@never_cache
@login_required
@read_access_required
def department_detail(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    dept_audits = dept.audits.all()
    dept_findings = Finding.objects.filter(audit__in=dept_audits)

    # ── Chart data: raw Python integers inlined into template ───────────
    dd_critical = dept_findings.filter(severity='critical').count()
    dd_high     = dept_findings.filter(severity='high').count()
    dd_medium   = dept_findings.filter(severity='medium').count()
    dd_low      = dept_findings.filter(severity='low').count()

    dd_planned  = dept_audits.filter(status='planned').count()
    dd_ongoing  = dept_audits.filter(status='ongoing').count()
    dd_closed   = dept_audits.filter(status='closed').count()

    overdue_findings_list = [f for f in dept_findings if f.is_overdue]

    context = {
        'dept': dept,
        'dept_audits': dept_audits,
        'dept_findings': dept_findings,
        'open_findings': dept_findings.filter(status='open').count(),
        'dd_critical': dd_critical,
        'dd_high':     dd_high,
        'dd_medium':   dd_medium,
        'dd_low':      dd_low,
        'dd_planned':  dd_planned,
        'dd_ongoing':  dd_ongoing,
        'dd_closed':   dd_closed,
        'overdue_count': len(overdue_findings_list),
        'overdue_findings': overdue_findings_list,
        'closed_audits': dept_audits.filter(status='closed').count(),
    }
    return render(request, 'audits/department_detail.html', context)


# ── Critical Issues ───────────────────────────────────────────────────────────

@never_cache
@login_required
@read_access_required
def critical_issues(request):
    critical_findings = Finding.objects.filter(
        severity='critical'
    ).select_related(
        'audit', 'audit__department', 'audit__assigned_auditor'
    ).order_by('-created_at')

    today = date.today()
    critical_findings = list(critical_findings)
    for f in critical_findings:
        f.overdue = (f.target_closure_date < today and f.status != 'closed')

    context = {
        'findings': critical_findings,
        'page_title': 'Critical Issues',
        'total_count': len(critical_findings),
    }
    return render(request, 'audits/critical_issues.html', context)


# ── Overdue Items ─────────────────────────────────────────────────────────────

@never_cache
@login_required
@read_access_required
def overdue_items(request):
    today = date.today()

    # Overdue findings: target date passed, not closed
    overdue_findings = Finding.objects.filter(
        target_closure_date__lt=today
    ).exclude(status='closed').select_related(
        'audit', 'audit__department'
    ).order_by('target_closure_date')

    # Overdue audits: end_date passed, not closed
    overdue_audits = Audit.objects.filter(
        end_date__lt=today
    ).exclude(status='closed').select_related(
        'department', 'assigned_auditor'
    ).order_by('end_date')

    overdue_findings = list(overdue_findings)
    overdue_audits = list(overdue_audits)

    for f in overdue_findings:
        f.days_overdue = (today - f.target_closure_date).days
    for a in overdue_audits:
        a.days_overdue = (today - a.end_date).days

    context = {
        'overdue_findings': overdue_findings,
        'overdue_audits': overdue_audits,
        'findings_count': len(overdue_findings),
        'audits_count': len(overdue_audits),
        'page_title': 'Overdue Items',
    }
    return render(request, 'audits/overdue_items.html', context)


# ── Reports ───────────────────────────────────────────────────────────────────

@login_required
@manager_required
def generate_report(request, pk):
    audit = get_object_or_404(Audit, pk=pk)
    if audit.status != 'closed':
        messages.error(request, 'Reports can only be generated for closed audits.')
        return redirect('audit_detail', pk=audit.pk)

    report, created = AuditReport.objects.get_or_create(
        audit=audit,
        defaults={'generated_by': request.user}
    )

    notes_form = ReportNotesForm(request.POST or None, instance=report)
    if request.method == 'POST' and notes_form.is_valid():
        notes_form.save()
        messages.success(request, 'Report notes saved.')
        return redirect('generate_report', pk=audit.pk)

    context = {
        'audit': audit,
        'report': report,
        'notes_form': notes_form,
        'findings': audit.findings.all(),
    }
    return render(request, 'audits/report_preview.html', context)


@login_required
@manager_or_auditee_required
def download_report_pdf(request, pk):
    audit = get_object_or_404(Audit, pk=pk)

    # Auditees can only download reports for their own department
    try:
        profile = request.user.profile
        if profile.role == 'auditee_head':
            if audit.department.name != profile.department:
                messages.error(request, 'You can only download reports for your department.')
                return redirect('audit_list')
    except Exception:
        pass

    try:
        pdf_buffer = generate_audit_pdf(audit)
        pdf_bytes = pdf_buffer.read()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        safe_title = audit.title.replace(' ', '_').replace('/', '-')[:50]
        filename = f'AuditShield_Report_{safe_title}_{audit.pk}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_bytes)
        return response
    except Exception as e:
        messages.error(request, f'PDF generation failed: {str(e)}')
        return redirect('audit_detail', pk=pk)


# ── User Profile ──────────────────────────────────────────────────────────────

@login_required
def user_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('user_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=request.user)

    context = {
        'profile': profile,
        'form': form,
        'page_title': 'My Profile',
        'last_login': request.user.last_login,
    }
    return render(request, 'audits/user_profile.html', context)


# ── Change Password ───────────────────────────────────────────────────────────

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                'Your password has been updated successfully. '
                'Please use your new password next time you log in.'
            )
            return redirect('user_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    # Apply Bootstrap classes to all form fields
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    context = {
        'form': form,
        'page_title': 'Change Password',
    }
    return render(request, 'audits/change_password.html', context)


# ── Access Denied ─────────────────────────────────────────────────────────────

def access_denied(request):
    return render(request, 'audits/access_denied.html', status=403)
