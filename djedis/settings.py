from __future__ import unicode_literals
from django.conf import settings

try:
    settings.configure()
except RuntimeError:
    pass

DEFAULT_CACHES = {
    'default': {
        'BACKEND': 'djedis.backend.RedisCache',
        'LOCATION': [
            'redis://localhost:6379/0',
            'redis://localhost:6379/2',
        ],
        'OPTIONS': {

        }
    }
}

CACHES = getattr(settings, 'CACHES', DEFAULT_CACHES)

DEFAULT_TIMEOUT = getattr(CACHES, 'OPTIONS', {}).get('DEFAULT_TIMEOUT', 60 * 15)
DEFAULT_MIN_LENGTH_COMPRESS = getattr(CACHES, 'OPTIONS', {}).get('DEFAULT_MIN_LENGTH_COMPRESS', 10)
