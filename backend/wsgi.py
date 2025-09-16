import os
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Auto-apply migrations on startup (useful when the platform skips running `migrate`)
try:
    import django
    from django.core.management import call_command
    django.setup()
    # run_syncdb helps create tables for apps without migrations (if any)
    call_command('migrate', interactive=False, run_syncdb=True)
except Exception as exc:
    logging.getLogger(__name__).exception('Auto-migrate on WSGI startup failed: %s', exc)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()