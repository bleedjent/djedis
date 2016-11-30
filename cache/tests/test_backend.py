from unittest import TestCase
from django.conf import settings
from django.core.cache import cache
settings.configure()

from cache.settings import DEFAULT_CACHES
from cache.backend import RedisCache

settings['CACHES'] = DEFAULT_CACHES


class RedisDjangoBackendTestCase(TestCase):

    def setUp(self):
        self.cache = RedisCache()

    def test__set(self):
        pass