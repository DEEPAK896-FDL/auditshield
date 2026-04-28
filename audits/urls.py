from django.urls import path
from django.views.generic import RedirectView, TemplateView
from . import views

urlpatterns = [
    path('',                    TemplateView.as_view(template_name='audits/landing.html'), name='landing'),
    path('login/',              views.login_view,           name='login'),
    path('logout/',             views.logout_view,          name='logout'),
    path('dashboard/',          views.dashboard,            name='dashboard'),
    path('audits/',             views.audit_list,           name='audit_list'),
    path('audits/create/',      views.audit_create,         name='audit_create'),
    path('audits/<int:pk>/',    views.audit_detail,         name='audit_detail'),
    path('audits/<int:pk>/edit/', views.audit_edit,         name='audit_edit'),
    path('audits/<int:pk>/findings/create/', views.finding_create, name='finding_create'),
    path('findings/',           views.finding_list,         name='finding_list'),
    path('findings/<int:pk>/',  views.finding_detail,       name='finding_detail'),
    path('findings/<int:pk>/edit/', views.finding_edit,     name='finding_edit'),
    path('findings/<int:pk>/close/', views.finding_close,   name='finding_close'),
    path('departments/',        views.department_analytics, name='department_analytics'),
    path('departments/<int:pk>/', views.department_detail,  name='department_detail'),
    path('audits/<int:pk>/report/',     views.generate_report,     name='generate_report'),
    path('audits/<int:pk>/report/pdf/', views.download_report_pdf, name='download_report_pdf'),
    path('critical-issues/',    views.critical_issues,      name='critical_issues'),
    path('overdue/',            views.overdue_items,        name='overdue_items'),
    path('profile/',            views.user_profile,         name='user_profile'),
    path('change-password/',    views.change_password,      name='change_password'),
    path('access-denied/',      views.access_denied,        name='access_denied'),
]
