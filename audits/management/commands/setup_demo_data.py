import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from audits.models import UserProfile, Department, Audit, Finding


class Command(BaseCommand):
    help = 'Creates demo data for AuditShield'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Setting up AuditShield demo data...'))

        # ── Users ──────────────────────────────────────────────────────────
        admin_user, created = User.objects.get_or_create(username='admin')
        if created or not admin_user.is_superuser:
            admin_user.set_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.first_name = 'Admin'
            admin_user.last_name = 'User'
            admin_user.email = 'admin@auditshield.com'
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Created/fixed user: admin / admin123'))
        profile_admin, _ = UserProfile.objects.get_or_create(user=admin_user)
        profile_admin.role = 'audit_manager'
        profile_admin.save()

        manager1, created = User.objects.get_or_create(username='manager1')
        if created:
            manager1.set_password('demo1234')
            manager1.first_name = 'James'
            manager1.last_name = 'Mitchell'
            manager1.email = 'james.mitchell@auditshield.com'
            manager1.is_staff = False
            manager1.is_superuser = False
            manager1.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Created user: manager1 / demo1234'))
        profile_m1, _ = UserProfile.objects.get_or_create(user=manager1)
        profile_m1.role = 'audit_manager'
        profile_m1.save()

        auditee1, created = User.objects.get_or_create(username='auditee1')
        if created:
            auditee1.set_password('demo1234')
            auditee1.first_name = 'Sarah'
            auditee1.last_name = 'Chen'
            auditee1.email = 'sarah.chen@auditshield.com'
            auditee1.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Created user: auditee1 / demo1234'))
        profile_a1, _ = UserProfile.objects.get_or_create(user=auditee1)
        profile_a1.role = 'auditee_head'
        profile_a1.department = 'IT Infrastructure'
        profile_a1.save()

        auditee2, created = User.objects.get_or_create(username='auditee2')
        if created:
            auditee2.set_password('demo1234')
            auditee2.first_name = 'Robert'
            auditee2.last_name = 'Patel'
            auditee2.email = 'robert.patel@auditshield.com'
            auditee2.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Created user: auditee2 / demo1234'))
        profile_a2, _ = UserProfile.objects.get_or_create(user=auditee2)
        profile_a2.role = 'auditee_head'
        profile_a2.department = 'Finance & Accounting'
        profile_a2.save()


        # ── Departments ────────────────────────────────────────────────────
        dept_it, _ = Department.objects.get_or_create(
            name='IT Infrastructure',
            defaults={
                'description': 'Manages all IT systems, network infrastructure, servers, and cybersecurity.',
                'head_user': auditee1,
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Department: IT Infrastructure'))

        dept_finance, _ = Department.objects.get_or_create(
            name='Finance & Accounting',
            defaults={
                'description': 'Oversees financial reporting, accounts payable/receivable, and budget management.',
                'head_user': auditee2,
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Department: Finance & Accounting'))

        dept_hr, _ = Department.objects.get_or_create(
            name='Human Resources',
            defaults={'description': 'Manages employee relations, recruitment, and compliance with labor laws.'}
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Department: Human Resources'))

        dept_ops, _ = Department.objects.get_or_create(
            name='Operations & Logistics',
            defaults={'description': 'Coordinates supply chain, vendor management, and operational processes.'}
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Department: Operations & Logistics'))

        today = datetime.date.today()

        # ── Audits ─────────────────────────────────────────────────────────
        audit1, created = Audit.objects.get_or_create(
            title='Q1 2025 IT Security Audit',
            defaults={
                'department': dept_it,
                'assigned_auditor': manager1,
                'created_by': admin_user,
                'start_date': today - datetime.timedelta(days=90),
                'end_date': today - datetime.timedelta(days=30),
                'status': 'closed',
                'objectives': 'Evaluate effectiveness of security controls, access management, and incident response procedures.',
                'scope': 'Network infrastructure, active directory, endpoint security, and firewall configurations.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Audit: {audit1.title}'))

        audit2, created = Audit.objects.get_or_create(
            title='Financial Controls Review 2025',
            defaults={
                'department': dept_finance,
                'assigned_auditor': manager1,
                'created_by': admin_user,
                'start_date': today - datetime.timedelta(days=20),
                'end_date': today + datetime.timedelta(days=30),
                'status': 'ongoing',
                'objectives': 'Review internal financial controls, segregation of duties, and compliance with GAAP.',
                'scope': 'General ledger, accounts payable, accounts receivable, payroll processing.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Audit: {audit2.title}'))

        audit3, created = Audit.objects.get_or_create(
            title='HR Compliance & Data Privacy Audit',
            defaults={
                'department': dept_hr,
                'assigned_auditor': manager1,
                'created_by': admin_user,
                'start_date': today + datetime.timedelta(days=10),
                'end_date': today + datetime.timedelta(days=60),
                'status': 'planned',
                'objectives': 'Assess compliance with data privacy regulations and HR process controls.',
                'scope': 'Employee records management, onboarding/offboarding procedures, GDPR compliance.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Audit: {audit3.title}'))

        audit4, created = Audit.objects.get_or_create(
            title='Supply Chain & Vendor Risk Assessment',
            defaults={
                'department': dept_ops,
                'assigned_auditor': manager1,
                'created_by': admin_user,
                'start_date': today - datetime.timedelta(days=10),
                'end_date': today + datetime.timedelta(days=50),
                'status': 'ongoing',
                'objectives': 'Evaluate vendor management processes and supply chain risk mitigation strategies.',
                'scope': 'Top 10 vendors, procurement procedures, contract management, and contingency planning.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Audit: {audit4.title}'))

        # ── Findings ───────────────────────────────────────────────────────
        findings_data = [
            {
                'audit': audit1,
                'title': 'Unpatched Critical CVE Vulnerabilities',
                'description': 'Multiple servers running outdated software with known critical CVEs (CVSS 9.x). Patches not applied within the mandatory 30-day SLA.',
                'severity': 'critical',
                'recommendation': 'Implement an automated patch management system. Apply all critical patches within 72 hours of release. Conduct monthly vulnerability scans.',
                'target_closure_date': today - datetime.timedelta(days=10),  # overdue
                'status': 'open',
                'response_notes': '',
            },
            {
                'audit': audit1,
                'title': 'Weak Password Policy Enforcement',
                'description': 'Active Directory password policy does not enforce complexity requirements. 23% of user accounts use passwords shorter than 8 characters.',
                'severity': 'high',
                'recommendation': 'Enforce a minimum 12-character password policy with complexity requirements. Implement MFA for all privileged accounts within 30 days.',
                'target_closure_date': today - datetime.timedelta(days=5),  # overdue
                'status': 'in_progress',
                'response_notes': 'GPO has been updated to enforce new password policy. MFA rollout in progress for admin accounts.',
            },
            {
                'audit': audit1,
                'title': 'Inadequate Network Segmentation',
                'description': 'Development and production environments share the same network segment, creating a lateral movement risk.',
                'severity': 'high',
                'recommendation': 'Implement VLAN segmentation to isolate production systems. Deploy a next-gen firewall with application-layer inspection.',
                'target_closure_date': today + datetime.timedelta(days=30),
                'status': 'open',
            },
            {
                'audit': audit1,
                'title': 'Insufficient Logging and Monitoring',
                'description': 'Security event logs are not centralized. SIEM system coverage is less than 40% of critical assets.',
                'severity': 'medium',
                'recommendation': 'Expand SIEM coverage to all critical assets. Implement 24/7 SOC monitoring. Retain logs for minimum 12 months.',
                'target_closure_date': today + datetime.timedelta(days=60),
                'status': 'closed',
                'closed_at': today - datetime.timedelta(days=5),
                'response_notes': 'SIEM deployment completed. All critical assets now covered. Log retention configured for 13 months.',
            },
            {
                'audit': audit2,
                'title': 'Segregation of Duties Violation',
                'description': 'Three employees in accounts payable have both create and approve privileges for vendor payments, creating fraud risk.',
                'severity': 'critical',
                'recommendation': 'Immediately revoke dual-role access. Implement a 4-eyes principle for all payments above $10,000. Document compensating controls.',
                'target_closure_date': today + datetime.timedelta(days=15),
                'status': 'open',
            },
            {
                'audit': audit2,
                'title': 'Reconciliation Process Gaps',
                'description': 'Monthly bank reconciliations are completed 15-20 days after month-end, exceeding the 5-day policy requirement.',
                'severity': 'medium',
                'recommendation': 'Automate bank reconciliation using ERP integration. Establish escalation procedures for items outstanding beyond 3 days.',
                'target_closure_date': today + datetime.timedelta(days=45),
                'status': 'in_progress',
                'response_notes': 'ERP team engaged to develop automated reconciliation module. Expected completion in 6 weeks.',
            },
            {
                'audit': audit4,
                'title': 'No Formal Vendor Risk Assessment Process',
                'description': 'Critical vendors are onboarded without formal risk assessments. 8 of the top 10 vendors have no documented risk profile.',
                'severity': 'high',
                'recommendation': 'Develop a vendor risk assessment framework. All critical vendors (Tier 1) must complete annual security assessments.',
                'target_closure_date': today + datetime.timedelta(days=30),
                'status': 'open',
            },
            {
                'audit': audit4,
                'title': 'Contract Renewal Tracking Gaps',
                'description': 'No automated system tracks contract expiry dates. 3 contracts expired without renewal in the past 6 months.',
                'severity': 'low',
                'recommendation': 'Implement a contract lifecycle management (CLM) system with automated 90-day expiry notifications.',
                'target_closure_date': today + datetime.timedelta(days=60),
                'status': 'open',
            },
        ]

        for fd in findings_data:
            closed_at = fd.pop('closed_at', None)
            finding, created = Finding.objects.get_or_create(
                audit=fd['audit'],
                title=fd['title'],
                defaults=fd,
            )
            if created and closed_at:
                from django.utils import timezone as tz
                finding.closed_at = tz.make_aware(
                    datetime.datetime.combine(closed_at, datetime.time.min)
                )
                finding.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Finding: {finding.title}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 55))
        self.stdout.write(self.style.SUCCESS('  AuditShield demo data created successfully!'))
        self.stdout.write(self.style.SUCCESS('═' * 55))
        self.stdout.write('')
        self.stdout.write('  Login Credentials:')
        self.stdout.write('  ┌─────────────┬──────────────┬───────────────────┐')
        self.stdout.write('  │ Username    │ Password     │ Role              │')
        self.stdout.write('  ├─────────────┼──────────────┼───────────────────┤')
        self.stdout.write('  │ admin       │ admin123     │ Audit Manager     │')
        self.stdout.write('  │ manager1    │ demo1234     │ Audit Manager     │')
        self.stdout.write('  │ auditee1    │ demo1234     │ Auditee Head (IT) │')
        self.stdout.write('  │ auditee2    │ demo1234     │ Auditee Head (Fin)│')
        self.stdout.write('  └─────────────┴──────────────┴───────────────────┘')
        self.stdout.write('')
        self.stdout.write('  Open: http://127.0.0.1:8000/login/')
        self.stdout.write('')
