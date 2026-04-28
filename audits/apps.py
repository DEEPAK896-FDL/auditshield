from django.apps import AppConfig


class AuditsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audits'
    verbose_name = 'AuditShield'

    def ready(self):
        import audits.models  # noqa — ensures signals are registered
