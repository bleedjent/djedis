# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from random import choice
from hashlib import md5

if sys.version_info[0] < 3:
    integer_types = (int, long,)
else:
    integer_types = (int,)


def make_key(key, version=None):
    if version is not None:
        key = '{0}:{1}'.format(key, version)
    return key.encode('utf-8')


def chose_index(key, allowed_indexes):
    return allowed_indexes[0]
