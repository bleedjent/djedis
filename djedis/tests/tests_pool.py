from unittest import TestCase
from djedis.pool import RedisPoolFactory
from djedis.settings import CACHES, DEFAULT_CACHES

CACHES.update(DEFAULT_CACHES)


class PoolTestCase(TestCase):

    def setUp(self):
        self.pool = RedisPoolFactory()

    def test_issingleton(self):
        foo = RedisPoolFactory()
        self.assertIs(foo, self.pool)
