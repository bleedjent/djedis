from __future__ import unicode_literals
from redis.connection import ConnectionPool, HiredisParser
from redis.client import StrictRedis

from .settings import CACHES


class RedisPoolFactory(object):
    _instance = None

    __pools = {}

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not self.__pools:
            self._create_pools()

    def __getitem__(self, item):
        return self.__pools[item]

    def __contains__(self, item):
        return item in self.__pools

    def keys(self):
        return self.__pools.keys()

    @staticmethod
    def _create_pool(_url, **kwargs):
        return ConnectionPool.from_url(url=_url, parser_class=HiredisParser, **kwargs)

    def _create_pools(self):
        for backend in CACHES.values():
            for _url in backend.get('LOCATION', []):
                if _url not in self.__pools:
                    self.__pools[_url] = self._create_pool(_url)

    def get_pools(self, urls):
        return [self[index] for index in urls]

    def connect(self, urls):
        return {url: StrictRedis(connection_pool=self[url]) for url in urls}
