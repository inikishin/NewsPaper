from celery import shared_task
import sys
from datetime import datetime, timedelta

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from django.contrib.auth.models import User
from django.core.mail import send_mail

from .models import Post, Category, CategoryUser, PostCategory



@shared_task
def task_send_notification(category_qs, username, header, content):
    send_notification(category_qs, username, header, content)

@shared_task
def task_regular_notification():
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


def send_notification(category_qs, username, header, content):
    print("Subsribers: ")
    for category in category_qs:
        email_list = (i['user__email'] for i in list(CategoryUser.objects.filter(category=category).values('user__email')))

        html_content = render_to_string(
            'news/article_created.html',
            {
                'username': username,
                'category': category.category_name,
                'header': header,
                'content': content,
            }
        )

        # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
        msg = EmailMultiAlternatives(
            subject=f'{header}',
            body=content,  # это то же, что и message
            from_email='Chestman888@yandex.ru',
            to=list(email_list),  # это то же, что и recipients_list
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html
        #msg.send()  # отсылаем
