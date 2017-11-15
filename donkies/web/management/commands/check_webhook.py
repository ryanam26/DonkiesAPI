from django.core.management.base import BaseCommand
from finance.services.dwolla_api import DwollaAPI


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        dwa = DwollaAPI()
        webhook_subscription = dwa.app_token.get('webhook-subscriptions')
        print (webhook_subscription.body)
        if webhook_subscription.body['total'] > 0:
            print("Webhook already exists, exiting")
        else:
            request_body = {
                'url': 'http://api.donkies.co/v1/dwolla_webhook',
                'secret': 'secret'
            }
            subscript = dwa.app_token.post('webhook-subscriptions',
                                           request_body)
            print (subscript)
            print ("Created webhook on url")
