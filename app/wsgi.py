import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Добавьте эту строку:
static_map = /static=/app/staticfiles

application = get_wsgi_application()
