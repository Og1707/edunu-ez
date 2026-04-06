from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from auth.models import MagicLinkToken


class Command(BaseCommand):
    help = 'Elimina tokens magic link usados o caducados hace más de 24 horas.'

    def handle(self, *args, **options):
        limite = timezone.now() - timedelta(hours=24)
        borrados, _ = MagicLinkToken.objects.filter(
            used=True
        ).delete()
        antiguos, _ = MagicLinkToken.objects.filter(
            used=False,
            created_at__lt=limite
        ).delete()
        self.stdout.write(self.style.SUCCESS(
            f'Tokens usados borrados: {borrados}, tokens caducados borrados: {antiguos}'
        ))


# Sugerencia de automatización:
# cron: 0 * * * * cd /path/to/edunuñez_django/backend && ./venv/Scripts/python manage.py limpiar_tokens
# o celery beat: schedule = {'limpiar_tokens': {'task': 'django.core.management.call_command', 'schedule': crontab(minute=0), 'args': ('limpiar_tokens',)}}
