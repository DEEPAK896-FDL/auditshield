import functools
from django.shortcuts import redirect


def _get_role(user):
    """Return effective role for this user."""
    try:
        return user.profile.role  # 'audit_manager', 'auditee_head', 'observer'
    except Exception:
        return None


def manager_required(view_func):
    """Only audit_manager can access."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if _get_role(request.user) == 'audit_manager':
            return view_func(request, *args, **kwargs)
        return redirect('access_denied')
    return wrapper


def auditee_required(view_func):
    """Only auditee_head can access."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if _get_role(request.user) == 'auditee_head':
            return view_func(request, *args, **kwargs)
        return redirect('access_denied')
    return wrapper


def manager_or_auditee_required(view_func):
    """audit_manager and auditee_head can access. Observer is blocked."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        role = _get_role(request.user)
        if role in ('audit_manager', 'auditee_head'):
            return view_func(request, *args, **kwargs)
        return redirect('access_denied')
    return wrapper


def read_access_required(view_func):
    """All 3 roles can access (manager, auditee, observer)."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        role = _get_role(request.user)
        if role in ('audit_manager', 'auditee_head', 'observer'):
            return view_func(request, *args, **kwargs)
        return redirect('access_denied')
    return wrapper
