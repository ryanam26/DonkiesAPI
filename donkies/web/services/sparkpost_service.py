from sparkpost import SparkPost
from django.conf import settings


class SparkPostService:
    def __init__(self):
        self.api_key = settings.SPARKPOST_APIKEY

    def send_email(
            self, recipients, subject, text, html=None, from_email=None):
        """
        recipients can be passed as single email (string) or
        list of emails.
        """
        if from_email is None:
            from_email = settings.SPARKPOST_FROM_EMAIL

        if isinstance(recipients, str):
            recipients = [recipients]

        sparky = SparkPost(self.api_key)
        data = {
            'from_email': from_email,
            'recipients': recipients,
            'subject': subject,
            'text': text}
        if html:
            data['html'] = html

        return sparky.transmissions.send(**data)

    def check_response(self, response):
        """
        Returns bool.
        """
        if 'total_accepted_recipients' in response:
            if response['total_accepted_recipients'] > 0:
                return True
        return False
