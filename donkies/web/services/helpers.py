import hashlib
import os
import random
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
