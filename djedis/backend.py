# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache.backends.base import BaseCache

from djedis.settings import DEFAULT_TIMEOUT
from djedis.client import ShardClient


class RedisCache(BaseCache):

    def __init__(self, server, params):
        super(RedisCache, self).__init__(params)
        self._server = server
        self._params = params
        self._client = None

    @property
    def client(self):
        """
        Lazy client connection property.
        """
        if self._client is None:
            self._client = ShardClient(self._server, self._params, self)
        return self._client

    @property
    def client(self):
        return self.client()

    def get(self, key, default=None, version=None):
        return self.client.get(key, default=default, version=version)

    def get_many(self, *args, **kwargs):
        return self.client.get_many(*args, **kwargs)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        return self.client.set(key, value, timeout=timeout, version=version)

    def set_many(self, *args, **kwargs):
        return self.client.set_many(*args, **kwargs)

    def delete(self, key, version=None):
        return self.client.delete(key, version=version)

    def delete_pattern(self, *args, **kwargs):
        return self.client.delete_pattern(*args, **kwargs)

    def delete_many(self, *args, **kwargs):
        return self.client.delete_many(*args, **kwargs)

    def has_key(self, *args, **kwargs):
        return self.client.has_key(*args, **kwargs)

    def keys(self, *args, **kwargs):
        return self.client.keys(*args, **kwargs)