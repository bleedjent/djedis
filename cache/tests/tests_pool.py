from unittest import TestCase
from cache.pool import RedisPoolFactory
from cache.settings import CACHES, DEFAULT_CACHES

CACHES.update(DEFAULT_CACHES)


class PoolTestCase(TestCase):

    def setUp(self):
        self.pool = RedisPoolFactory()

    def test_issingleton(self):
        foo = RedisPoolFactory()
        self.assertIs(foo, self.pool)