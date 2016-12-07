# -*- coding: utf-8 -*-
import uuid
import random
from unittest import TestCase

from djedis.utils import make_key
from djedis.client import ShardClient
from djedis.settings import CACHES, DEFAULT_CACHES

CACHES.update(DEFAULT_CACHES)


class UtilsTestCase(TestCase):
    def setUp(self):
        self.default_params = DEFAULT_CACHES['default']
        self.client = ShardClient(
            servers=self.default_params['LOCATION'],
            params=self.default_params['OPTIONS']
        )
        self.keys = {}
        for i in range(1, 500):
            _key = 'for_keys:%s' % str(uuid.uuid4())
            self.keys[_key] = self.client.get_server_name(_key)
            self.client.set(_key, str(uuid.uuid4())*random.randint(2, 10))

    def test__make_key(self):
        fine_key = 'foo:1'
        self.assertIsInstance(make_key('foo', 1), str)
        self.assertEqual(make_key('foo', 1), fine_key)
        self.assertIsInstance(make_key(u'вот'), str)
        self.assertIsInstance(make_key(u'вот', 2), str)
