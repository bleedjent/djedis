import cPickle as pickle
import snappy

from .pool import get_connection_factory
from .settings import DEFAULT_TIMEOUT, DEFAULT_MIN_LENGTH_COMPRESS
from .utils import make_key, integer_types
from .hash_ring import HashRing


class ShardClient(object):
    _serializer = pickle

    def __init__(self, servers, params):
        self._servers = servers
        self._params = params

        self.connection_factory = get_connection_factory(options=self._params)
        self._ring = HashRing(self._servers)
        self._pool = self.connect()

    def connect(self):
        connection_dict = {}
        for name in self._servers:
            connection_dict[name] = self.connection_factory.connect(name)
        return connection_dict

    def get_client(self, key):
        name = self.get_server_name(key)
        return self._pool[name]

    def get_server_name(self, key):
        name = self._ring.get_node(key)
        return name

    @staticmethod
    def _can_compress(value):
        return isinstance(value, bool) or not isinstance(value, integer_types)

    def _compress(self, value):
        if self._can_compress(value) and len(value) > DEFAULT_MIN_LENGTH_COMPRESS:
            value = snappy.compress(str(value))
        return value

    def _decompress(self, value):
        try:
            value = snappy.decompress(value)
        except snappy.UncompressError:
            pass
        return value

    def _decode(self, value):
        """For get"""
        if value is not None:
            value = self._decompress(value)
            try:
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    value = self._serializer.loads(value)
            except (Exception,):
                return None
        return value

    def _encode(self, value):
        """For set"""
        if value is not None:
            if self._can_compress(value):
                value = self._serializer.dumps(value)
                value = self._compress(value)
        return value

    # PUBLIC
    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, nx=False, xx=False):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.set(key, str(self._encode(value)), ex=timeout, nx=nx, xx=xx)

    def get(self, key, default=None, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return self._decode(client.get(key)) or default

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

    def has_key(self, key, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.get(key) is not None
