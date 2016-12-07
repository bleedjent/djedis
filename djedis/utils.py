# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys

if sys.version_info[0] < 3:
    integer_types = (int, long,)
else:
    integer_types = (int,)


def make_key(key, version=None):
    if version is not None:
        key = '{0}:{1}'.format(key, version)
    return key.encode('utf-8')


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


class KeysHandler(object):

    def __init__(self, data, client):
        self._data = data
        self._client = client

    def __iter__(self):
        return self

    def next(self):
        for server, _gen in self._data.items():
            for key in _gen:
                yield key

    def __next__(self):  # for python 3 support
        return self.next()
