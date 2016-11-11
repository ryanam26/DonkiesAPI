import time
from celery.decorators import periodic_task
from celery.task.schedules import crontab
import datetime
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from .models import Emailer, Logging


# @periodic_task(run_every=crontab())
def send_email():
    """
    Runs every minute.
    Checks emails that haven't been sent - and send them.
    """
    q = Emailer.objects.filter(sent=False)
    for e in q:
        msg = EmailMultiAlternatives(
            e.subject, e.txt, e.email_from, [e.email_to])
        msg.attach_alternative(e.html, "text/html")

        try:
            msg.send()
            e.result = True
            e.report = 'OK'
        except Exception as e:
            e.result = False
            e.report = str(e)

        e.sent_at = datetime.datetime.now()
        e.sent = True
        e.save()

        time.sleep(3)


@periodic_task(run_every=crontab(minute=0, hour=0))
def clear_old_logs():
    """
    Removes old rows from Log
    """
    Logging.objects.filter(
        dt__lt=timezone.now() - datetime.timedelta(days=15)).delete()
