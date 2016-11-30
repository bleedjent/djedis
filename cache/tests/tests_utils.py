# -*- coding: utf-8 -*-
from hashlib import md5
from unittest import TestCase

from cache.utils import make_key, chose_index
from cache.pool import RedisPoolFactory
from cache.settings import CACHES, DEFAULT_CACHES

CACHES.update(DEFAULT_CACHES)


class UtilsTestCase(TestCase):

    def test__make_key(self):
        fine_key = md5('foo:1').hexdigest()
        self.assertIsInstance(make_key('foo', 1), str)
        self.assertEqual(make_key('foo', 1), fine_key)
        self.assertIsInstance(make_key(u'вот'), str)
        self.assertIsInstance(make_key(u'вот', 2), str)

    def test__chose_index(self):
        key1 = make_key('foo')
        key2 = make_key('bar')
        pool = RedisPoolFactory()
        _pool_keys = pool.keys()
        index1 = chose_index(key1, _pool_keys)
        index2 = chose_index(key2, _pool_keys)
        self.assertEqual(chose_index(key1, _pool_keys), index1)
        self.assertEqual(chose_index(key2, _pool_keys), index2)