import functools
import hashlib
import os
import random
import re
import string
import time
from datetime import datetime, timedelta


def get_md5(value):
    md5 = hashlib.md5()
    md5.update(str(value).encode())
    return md5.hexdigest()


def randstring(len):
    s = string.ascii_lowercase + string.digits
    return ''.join(random.sample(s, len))


def generate_filename():
    value = str(time.time()) + randstring(10)
    return get_md5(value)


def create_filename(filename):
    """
    Creates filename from filename.
    Uses random name for name itself
    and lowercase extension.
    """
    tup = os.path.splitext(filename)
    ext = tup[1].lower()
    return generate_filename() + ext


def to_camel(value):
    words = [word.capitalize() for word in value.split('_')]
    words[0] = words[0].lower()
    return ''.join(words)


def to_underscore(value):
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def rs_singleton(rs, key, exp=1800):
    """
    Redis singleton.
    rs - Redis server.
    key - key that used in Redis db.
    exp - expire time seconds, if fault (exception).
    """
    def deco(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if rs.get(key):
                return
            rs.set(key, 'true')
            rs.expire(key, exp)
            output = func(*args, **kwargs)
            rs.delete(key)
            return output
        return inner
    return deco


class cached:
    def __init__(self, *args, **kwargs):
        self.cached_function_responses = {}
        self.default_max_age = kwargs.get(
            'default_max_age', timedelta(seconds=0))

    def __call__(self, func):
        def inner(*args, **kwargs):
            max_age = kwargs.get('max_age', self.default_max_age)
            if not max_age or func not in self.cached_function_responses or \
                    (datetime.now() - self.cached_function_responses[func]['fetch_time'] > max_age):
                if 'max_age' in kwargs:
                    del kwargs['max_age']
                res = func(*args, **kwargs)
                self.cached_function_responses[func] = {
                    'data': res, 'fetch_time': datetime.now()}
            return self.cached_function_responses[func]['data']
        return inner
