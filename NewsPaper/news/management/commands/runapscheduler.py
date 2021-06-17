import logging
import sys
from datetime import datetime, timedelta

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.mail import send_mail

from news.models import Post, Category, CategoryUser, PostCategory
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    print(sys.path)
    users = User.objects.all()
    for u in users:
        cats = list(CategoryUser.objects.filter(user=u).values_list('category'))
        search_date = datetime.now() - timedelta(days=7)
        title_list = []
        for c in cats:
            posts = list(PostCategory.objects.filter(category=c, post__created__gt=search_date).values_list('post__title'))
            title_list = title_list + posts

        if len(title_list) > 0:
            title = f'Привет { u }, в твоих категориях появились новые статьи!'
            content = 'Список статей за последнюю неделю:\n'
            for t in title_list:
                content = content + f'     * { t[0] }\n'

        # отправляем письмо
        send_mail(
            subject=title,
            # имя клиента и дата записи будут в теме для удобства
            message=content,  # сообщение с кратким описанием проблемы
            from_email='Chestman888@yandex.ru',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
            recipient_list=[u.email]  # здесь список получателей. Например, секретарь, сам врач и т. д.
        )


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/10"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")