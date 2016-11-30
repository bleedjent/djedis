from __future__ import unicode_literals
from redis.connection import ConnectionPool
from redis.client import StrictRedis

from .settings import CACHES


class RedisPoolFactory(object):
    _instance = None

    __pools = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self.__pools is None:
            self.__pools = self._create_pools()

    @staticmethod
    def _create_pool(backend):
        return ConnectionPool.from_url(url=backend['LOCATION'])

    def _create_pools(self):
        return {key: self._create_pool(backend) for key, backend in CACHES.items()}

    def get_pool(self, index):
        return self.__pools[index]

    def connect(self, index):
        return StrictRedis(connection_pool=self.get_pool(index))

    def __getitem__(self, item):
        return self.__pools[item]
