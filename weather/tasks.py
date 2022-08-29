from celery import shared_task
from celery.utils.log import get_task_logger
#from django.contrib.auth.models import User
#from . import models


logger = get_task_logger(__name__)


@shared_task
def sample_task():
    from weather.models import User, Subscription, Weather
    logger.info("The sample task just ran!!!!!!!!!!!!!!!!!!!!")
    for user in User.objects.all():
        logger.info(f"USER: {user.username}")
        if user.subscribed.all().count():  # WORKS
            logger.info(f"USER: {user.username} HAS SUBS")
            # CHECK HOW OFTEN
            # SEND EMAILS HERE


