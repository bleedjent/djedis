import snappy
from collections import defaultdict

from .pool import RedisPoolFactory
from .settings import DEFAULT_TIMEOUT, DEFAULT_MIN_LENGTH_COMPRESS
from .utils import make_key, integer_types
from .hash_ring import HashRing

try:
    import cPickle as pickle
except (ImportError,):
    import pickle


class ShardClient(object):
    _serializer = pickle

    def __init__(self, servers, params):
        self._servers = servers
        if not isinstance(servers, list):
            self._servers = [servers]

        self._params = params

        self._pool_factory = RedisPoolFactory()
        self._pool = {name: self._pool_factory.get_connect(name) for name in self._servers}

        self._ring = None
        if len(self._servers) > 1:
            self._ring = HashRing(self._servers)

    def get_server_name(self, key):
        if self._ring is not None:
            return self._ring.get_node(key)
        return self._servers[0]

    def get_client(self, key):
        return self._pool[self.get_server_name(key)]

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
        value = self._decode(client.get(key))
        return value if value is not None else default

    def delete(self, key, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.delete(*(key,))

    def publish(self, channel, msg):
        client = self.get_client(channel)
        return client.publish(channel, msg)

    #  batch commands
    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        for key, value in data.items():
            self.set(key, value, timeout, version=version)

    def get_many(self, keys, version=None):
        _result = {}
        # prepare all keys
        keys = tuple(make_key(key, version=version) for key in keys)
        # filter by nodes
        _key_nodes = defaultdict(list)
        for _key in keys:
            _key_nodes[self.get_server_name(_key)].append(_key)

        for server, client in self._pool.items():
            _keys = _key_nodes.get(server, None)
            if _keys is not None:
                _result.update(dict(zip(_keys, [self._decode(v) for v in client.mget(keys)])))
        return _result

    def delete_many(self, keys, version=None):
        res = 0
        keys = tuple(make_key(key, version=version) for key in keys)
        for client in self._pool.values():
            res += client.delete(*set(keys))
        return res

    def keys(self, pattern='*'):
        for server, client in self._pool.items():
            for key in client.scan_iter(match=pattern):
                yield key

    def delete_pattern(self, pattern):
        for key in self.keys(pattern):
            client = self.get_client(key)
            client.delete(*(key,))

    def has_key(self, key, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.get(key) is not None

    def clear(self):
        for client in self._pool.values():
            client.flushall()

    def incr(self, key, delta=1, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.incr(key, delta)