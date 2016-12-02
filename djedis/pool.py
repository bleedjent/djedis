from __future__ import unicode_literals
from redis.connection import ConnectionPool
from redis.client import StrictRedis

try:
    import hiredis
    from redis.connection import HiredisParser as Parser
except ImportError:
    from redis.connection import DefaultParser as Parser


class RedisPoolFactory(object):
    _instance = None

    __pools = {}

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __contains__(self, item):
        return item in self.__pools

    def __getitem__(self, server):
        if server not in self:
            self.__pools[server] = ConnectionPool.from_url(url=server, parser_class=Parser)
        return self.__pools[server]

    def get_connect(self, server):
        return StrictRedis(connection_pool=self[server])
