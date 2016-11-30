# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from random import choice
from hashlib import md5


def make_key(key, version=None):
    if version is not None:
        key = '{0}:{1}'.format(key, version)
    return md5(key.encode('utf-8')).hexdigest()


def chose_index(key, allowed_indexes):
    return choice(allowed_indexes)
