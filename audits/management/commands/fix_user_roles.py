from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from audits.models import UserProfile


class Command(BaseCommand):
    help = 'Fix UserProfile roles for all AuditShield users'

    def handle(self, *args, **options):
        self.stdout.write('Fixing user roles...\n')

        # admin: observer role — read-only audit system access
        try:
            admin = User.objects.get(username='admin')
            admin.is_superuser = False  # Remove superuser — uses audit system
            admin.is_staff = True       # Keep staff for identification only
            admin.save()
            profile, _ = UserProfile.objects.get_or_create(user=admin)
            profile.role = 'observer'
            profile.save()
            self.stdout.write(
                self.style.SUCCESS(
                    'admin → role=observer (read-only audit access)'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('User "admin" not found'))

        # manager1: audit_manager role, NOT superuser
        try:
            manager1 = User.objects.get(username='manager1')
            manager1.is_superuser = False
            manager1.is_staff = False
            manager1.save()
            profile, _ = UserProfile.objects.get_or_create(user=manager1)
            profile.role = 'audit_manager'
            profile.department = ''
            profile.save()
            self.stdout.write(
                self.style.SUCCESS('manager1 → role=audit_manager ✓')
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('User "manager1" not found'))

        # auditee1: auditee_head, IT Infrastructure
        try:
            auditee1 = User.objects.get(username='auditee1')
            auditee1.is_superuser = False
            auditee1.is_staff = False
            auditee1.save()
            profile, _ = UserProfile.objects.get_or_create(user=auditee1)
            profile.role = 'auditee_head'
            profile.department = 'IT Infrastructure'
            profile.save()
            self.stdout.write(
                self.style.SUCCESS(
                    'auditee1 → role=auditee_head, dept=IT Infrastructure ✓'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('User "auditee1" not found'))

        # auditee2: auditee_head, Finance & Accounting
        try:
            auditee2 = User.objects.get(username='auditee2')
            auditee2.is_superuser = False
            auditee2.is_staff = False
            auditee2.save()
            profile, _ = UserProfile.objects.get_or_create(user=auditee2)
            profile.role = 'auditee_head'
            profile.department = 'Finance & Accounting'
            profile.save()
            self.stdout.write(
                self.style.SUCCESS(
                    'auditee2 → role=auditee_head, dept=Finance & Accounting ✓'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('User "auditee2" not found'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            '✅ All roles fixed. Run: python manage.py runserver'
        ))
