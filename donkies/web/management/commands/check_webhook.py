from django.core.management.base import BaseCommand, CommandError
from finance.services.dwolla_api import DwollaAPI


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        dwa = DwollaAPI()
        webhook_subscription = dwa.app_token.get('webhook-subscriptions')
        if webhook_subscription.body['total'] > 0:
            print("Webhook already exists, exiting")
        else:
            request_body = {
                  'url': 'http://myapplication.com/webhooks',
                  'secret': 'sshhhhhh'
            }
            retries = dwa.app_token.post('webhook-subscriptions', request_body)
            print ("Created webhook on url")