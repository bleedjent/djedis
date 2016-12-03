import uuid
import random
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
            self.keys[_key] = self.client.get_server_name(_key)
            self.client.set(_key, str(uuid.uuid4())*random.randint(2, 10))

    def test_get_server_name(self):
        for key, index in self.keys.items():
            self.assertEqual(self.client.get_server_name(key), index)

    def test__has_key(self):
        self.client.set('foo', 'test_value', 600)
        self.assertTrue(self.client.has_key('foo'))
        self.assertFalse(self.client.has_key('foo'*random.randint(2, 4)))

    def test__get(self):
        for key, index in self.keys.items():
            self.assertIsNotNone(self.client.get(key))

    def test__get_many(self):
        self.client.set_many(self.keys)
        result = self.client.get_many(self.keys.keys())
        self.assertIsInstance(result, dict)
        self.assertTrue(any(v in self.keys.values() or None for v in result.values()))
        self.assertTrue(any(k in self.keys.keys() for k in result.keys()))

    def test__set(self):
        self.assertTrue(any(self.client.set(key, 'test_value') for key in self.keys.keys()))
        self.assertTrue(any(self.client.get(key) == 'test_value' for key in self.keys.keys()))

    def test__delete(self):
        _delete_key = random.choice(self.keys.keys())
        self.client.delete(_delete_key)
        self.assertIsNone(self.client.get(_delete_key))