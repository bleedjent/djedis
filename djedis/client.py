import cPickle as pickle
from uhashring import HashRing
from .pool import RedisPoolFactory
from .settings import DEFAULT_TIMEOUT
from .utils import make_key, integer_types


class ShardClient(object):
    _serializer = pickle

    def __init__(self, servers, params):
        self._server = servers
        self._params = params
        self._pool = RedisPoolFactory().connect(servers)
        self._hashring = HashRing(nodes=servers)

    def get_client(self, key):
        return self._pool[self._get_pool_index(key)]

    def _get_pool_index(self, key):
        return self._hashring.get_node(key)

    def _decode(self, value):
        """For get"""
        if value is not None:
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = self._serializer.loads(value)
        return value

    def _encode(self, value):
        """For set"""
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, integer_types):
                return self._serializer.dumps(value)
        return value

    # PUBLIC
    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, nx=False, xx=False):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.set(key, self._encode(value), ex=timeout, nx=nx, xx=xx)

    def get(self, key, default=None, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return self._decode(client.get(key))

    def delete(self, key, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.delete(*(key,))

    #  batch commands
    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        for key, value in data.items():
            self.set(key, value, timeout, version=version)

    def get_many(self, keys, version=None):
        _result = []
        keys = tuple(make_key(key, version=version) for key in keys)
        for client in self._pool.values():
            _result.extend([self._decode(v) for v in client.mget(keys)])
        return _result

    def delete_many(self, keys, version=None):
        res = 0
        keys = tuple(make_key(key, version=version) for key in keys)
        for client in self._pool.values():
            res += client.delete(*keys)
        return res

    def keys(self, pattern='*'):
        _keys = set()
        for client in self._pool.values():
            _keys.update(client.keys(pattern))
        return _keys

    def delete_pattern(self, pattern):
        return self.delete_many(self.keys(pattern))
