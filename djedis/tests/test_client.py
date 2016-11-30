import uuid
from unittest import TestCase
from djedis.client import ShardClient
from djedis.settings import DEFAULT_CACHES


class ClientTestCase(TestCase):

    def setUp(self):
        self.default_params = DEFAULT_CACHES['default']
        self.client = ShardClient(
            servers=self.default_params['LOCATION'],
            params=self.default_params['OPTIONS']
        )
        self.keys = {}
        for i in range(1, 5):
            _key = str(uuid.uuid4())
            self.keys[_key] = self.client._get_pool_index(_key)
            self.client.set(_key, i)

    def test_get_pool_index(self):
        for key, index in self.keys.items():
            self.assertEqual(self.client._get_pool_index(key), index)

    def test__get(self):
        for key, index in self.keys.items():
            self.assertIsNotNone(self.client.get(key))

    def test__set(self):
        self.assertTrue(any(self.client.set(key, 'test_value') for key in self.keys.keys()))
        self.assertTrue(any(self.client.get(key) == 'test_value' for key in self.keys.keys()))
