import functools
import hashlib
import logging
import os
import random
import re
import string
import time
from datetime import datetime, timedelta
from finance.services.dwolla_api import DwollaAPI
from django.apps import apps


logger = logging.getLogger('app')


def round_to_prev5(n):
    """
    Round to nearest prev 5, 10, 15 etc.
    Examples: Round 12 to 10
              Round 19 to 15.
    """
    return n + (5 - n) % 5 - 5


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


def production(is_production):
    """
    Run decorated function if is_production is True
    """
    def deco(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if not is_production:
                return
            output = func(*args, **kwargs)
            return output
        return inner
    return deco


def catch_exception(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            raise Exception(e)
    return inner


class cached:
    def __init__(self, *args, **kwargs):
        self.cached_function_responses = {}
        self.default_max_age = kwargs.get(
            'default_max_age', timedelta(seconds=0))

    def __call__(self, func):
        def inner(*args, **kwargs):
            max_age = kwargs.get('max_age', self.default_max_age)
            if not max_age or func not in self.cached_function_responses \
             or (datetime.now() - self.cached_function_responses[func]['fetch_time'] > max_age):
                if 'max_age' in kwargs:
                    del kwargs['max_age']
                res = func(*args, **kwargs)
                self.cached_function_responses[func] = {
                    'data': res, 'fetch_time': datetime.now()}
            return self.cached_function_responses[func]['data']
        return inner


def create_webhook_context(data):
    dwa = DwollaAPI()
    value = {}
    Customer = apps.get_model("bank", "Customer")
    if data['topic'] == "customer_created" \
            or data['topic'] == "customer_verified" \
            or data['topic'] == "customer_suspended" \
            or data['topic'] == "customer_activated" \
            or data['topic'] == "customer_deactivated":
        customer_url = data['_links']['customer']['href']
        customer_id = dwa.app_token.get(customer_url).body['id']
        email = Customer.objects.get(dwolla_id=customer_id).email
        value.update({"email": email})
        return value
    if data['topic'] == "customer_funding_source_added" \
        or data['topic'] == "customer_funding_source_removed" \
            or data['topic'] == "customer_funding_source_verified":
        source_url = dwa.get_balance_funding_source(data['resourceId'])
        source = dwa.app_token.get(source_url).body
        value.update({"bankName": source['bankName']})
        value.update({"account_identifier": source['name']})
        value.update({"date": source['created']})
        customer_url = data['_links']['customer']['href']
        customer_id = dwa.app_token.get(customer_url).body['id']
        email = Customer.objects.get(dwolla_id=customer_id).email
        value.update({"email": email})
        return value
    if data['topic'] == "customer_bank_transfer_created" \
        or data['topic'] == "customer_bank_transfer_cancelled" \
        or data['topic'] == "customer_bank_transfer_failed" \
            or data['topic'] == "customer_bank_transfer_completed":
        transfer_url = dwa.get_transfer_url(data['resourceId'])
        transfer = dwa.app_token.get(transfer_url).body
        value.update({'transfer_type': transfer['status']})
        value.update({'amount_currency': transfer['amount']['currency']})
        value.update({'amount_value': transfer['amount']['value']})
        value.update({'transfer_date': transfer['created']})
        value.update(
            {'destination': transfer['_links']['destination']['href']})
        customer_url = data['_links']['customer']['href']
        customer_id = dwa.app_token.get(customer_url).body['id']
        email = Customer.objects.get(dwolla_id=customer_id).email
        value.update({"email": email})
        return value
    if data['topic'] == "customer_transfer_created" \
        or data['topic'] == "customer_transfer_cancelled" \
        or data['topic'] == "customer_transfer_failed" \
            or data['topic'] == "customer_transfer_completed":
        transfer_url = dwa.get_transfer_url(data['resource_id'])
        transfer = dwa.app_token.get(transfer_url).body
        value.update({'transfer_type': transfer['status']})
        value.update({'amount_currency': transfer['amount']['currency']})
        value.update({'amount_value': transfer['amount']['value']})
        value.update({'transfer_date': transfer['created']})
        value.update(
            {'destination': transfer['_links']['destination']['href']})
        customer_url = data['_links']['customer']['href']
        customer_id = dwa.app_token.get(customer_url).body['id']
        email = Customer.objects.get(dwolla_id=customer_id).email
        value.update({"email": email})
        return value
