from .pool import RedisPoolFactory
from .settings import DEFAULT_TIMEOUT
from .utils import make_key, chose_index


class ShardClient(object):

    def __init__(self, servers, params, backend):
        self._backend = backend
        self._server = servers
        self._params = params
        self._pool = RedisPoolFactory()
        self._allowed_pools_keys = self._pool.keys()

    def get_client(self, key):
        return self._pool(self._get_pool_index(key))

    def _get_pool_index(self, key):
        return chose_index(key, self._allowed_pools_keys)

    # PUBLIC
    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, client=None):
        if client is None:
            key = make_key(key, version=version)
            client = self.get_client(key)

        return client.add(key=key, value=value, version=version, client=client, timeout=timeout)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, client=None, nx=False):
        """
        Persist a value to the cache, and set an optional expiration time.
        """
        if client is None:
            key = make_key(key, version=version)
            client = self.get_server(key)

        return super(ShardClient, self).set(key=key, value=value,
                                            timeout=timeout, version=version,
                                            client=client, nx=nx)

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Set a bunch of values in the cache at once from a dict of key/value
        pairs. This is much more efficient than calling set() multiple times.

        If timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.
        """
        for key, value in data.items():
            self.set(key, value, timeout, version=version)

    def get(self, key, default=None, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.get(key=key, default=default, version=version)

    def get_many(self, keys, version=None):
        _result = []
        for key in keys:
            _result.append(self.get(key, version=version))
        return _result

    def delete(self, key, version=None):
        key = make_key(key, version=version)
        client = self.get_client(key)
        return client.delete(key=key, version=version, client=client)

    def delete_many(self, keys, version=None):
        res = 0
        for key in keys:
            res += self.delete(key, version=version)
        return res

    def delete_pattern(self, pattern):
        return ''

