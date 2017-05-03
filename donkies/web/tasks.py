import datetime
import time
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.utils import timezone
from web.models import Emailer, Logging, Alert
from web.services.sparkpost_service import SparkPostService


@periodic_task(run_every=crontab())
def send_email():
    """
    Runs every minute.
    Checks emails that haven't been sent - and send them.
    """
    sps = SparkPostService()
    for em in Emailer.objects.filter(sent=False):
        response = sps.send_email(
            em.email_to,
            em.subject,
            em.txt,
            html=em.html
        )

        if sps.check_response(response):
            em.result = True
        else:
            em.result = False

        em.sent = True
        em.sent_at = timezone.now()
        em.report = str(response)
        em.save()

        time.sleep(1)


@periodic_task(run_every=crontab())
def send_alert():
    """
    Alert for admin.
    Runs every minute.
    Checks not processed alerts and send them.
    """
    for alert in Alert.objects.filter(is_processed=False):
        alert.send()
        time.sleep(1)


@periodic_task(run_every=crontab(minute=0, hour=0))
def clear_old_logs():
    """
    Removes old rows from Log
    """
    Logging.objects.filter(
        dt__lt=timezone.now() - datetime.timedelta(days=15)).delete()
