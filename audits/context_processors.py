from datetime import date


def role_nav_context(request):
    if not request.user.is_authenticated:
        return {}
    try:
        from audits.models import Finding
        profile = request.user.profile
        role = profile.role
        today = date.today()

        if role == 'audit_manager':
            overdue_count = Finding.objects.filter(
                target_closure_date__lt=today
            ).exclude(status='closed').count()
            return {
                'user_role': 'audit_manager',
                'is_manager': True,
                'is_auditee': False,
                'is_observer': False,
                'user_department': '',
                'overdue_count': overdue_count,
            }

        elif role == 'auditee_head':
            overdue_count = Finding.objects.filter(
                target_closure_date__lt=today,
                audit__department__name=profile.department
            ).exclude(status='closed').count()
            return {
                'user_role': 'auditee_head',
                'is_manager': False,
                'is_auditee': True,
                'is_observer': False,
                'user_department': profile.department,
                'overdue_count': overdue_count,
            }

        elif role == 'observer':
            overdue_count = Finding.objects.filter(
                target_closure_date__lt=today
            ).exclude(status='closed').count()
            return {
                'user_role': 'observer',
                'is_manager': False,
                'is_auditee': False,
                'is_observer': True,
                'user_department': '',
                'overdue_count': overdue_count,
            }

        return {
            'user_role': '', 'is_manager': False,
            'is_auditee': False, 'is_observer': False,
            'user_department': '', 'overdue_count': 0,
        }

    except Exception:
        return {
            'user_role': '', 'is_manager': False,
            'is_auditee': False, 'is_observer': False,
            'user_department': '', 'overdue_count': 0,
        }
