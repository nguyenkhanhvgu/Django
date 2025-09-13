"""
WSGI config for advanced_patterns project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advanced_patterns.settings')

application = get_wsgi_application()