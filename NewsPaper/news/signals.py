from django.db.models.signals import pre_save
from django.dispatch import receiver # импортируем нужный декоратор
from django.core.mail import mail_managers
from .models import Post

from datetime import datetime, timedelta

# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(pre_save, sender=Post)
def check_max_post_today(sender, instance, **kwargs):
    date_from = datetime.now() - timedelta(days=1)
    post_count_today = len(Post.objects.filter(author=instance.author, created__gte=date_from))

    if post_count_today >= 3:
        raise Exception('More than 3 post today created')