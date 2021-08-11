from datetime import datetime

from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView
from django.core.paginator import Paginator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required

from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст

from .models import Post, Category, CategoryUser
from django.db.models.signals import pre_save

from .filters import PostFilter
from .forms import PostForm
from .signals import check_max_post_today
from .tasks import task_send_notification
import logging

pre_save.connect(check_max_post_today, sender=Post)
logger = logging.getLogger('django.security')

@login_required
def subscribe(request):
    user = request.user
    category = request.GET['category']

    rel = CategoryUser.objects.get(category=Category.objects.get(pk=category), user=user)
    if (rel == None):
        rel = CategoryUser(category= Category.objects.get(pk=category),
                     user=user)
        rel.save()
    return redirect(request.META['HTTP_REFERER'])

def category_view(request, pk):
    context = {
        'newslist': Post.objects.filter(category=pk),
        'category': Category.objects.get(pk=pk)
    }
    logger.error(f"Open category_view with pk:{pk}")
    return render(request=request, template_name='news/news_list.html', context=context)

class NewsList(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'newslist'
    ordering = ['-created']
    paginate_by = 5
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['categories'] = Category.objects.all()
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        err = False
        if form.is_valid():
            try:
                form.save()
                task_send_notification.apply_async(form.cleaned_data['category'],
                                       request.user.username,
                                       form.cleaned_data['title'],
                                       form.cleaned_data['content'])
                # send_notification(form.cleaned_data['category'],
                #                   request.user.username,
                #                   form.cleaned_data['title'],
                #                   form.cleaned_data['content'])
            except Exception:
                err = True

        if err:
            return HttpResponse("Слишком много статей на сегодня")
        else:
            return super().get(request, *args, **kwargs)

class NewsDetails(DetailView):
    model = Post
    template_name = 'news/news.html'
    context_object_name = 'news'

class NewsSearch(ListView):
    model = Post
    template_name = 'news/news_search.html'
    context_object_name = 'newslist'
    ordering = ['-created']
    paginate_by = 1

    def get_context_data(self,
                         **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET,
                                          queryset=self.get_queryset())
        return context

class NewsCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    template_name = 'news/news_create.html'
    form_class = PostForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            task_send_notification.apply_async(form.cleaned_data['category'],
                                               request.user.username,
                                               form.cleaned_data['title'],
                                               form.cleaned_data['content'])
            # send_notification(form.cleaned_data['category'],
            #                   request.user.username,
            #                   form.cleaned_data['title'],
            #                   form.cleaned_data['content'])

        return super().get(request, *args, **kwargs)

class NewsUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    template_name = 'news/news_create.html'
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

class NewsDeleteView(DeleteView):
    template_name = 'news/news_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


# Отправка email
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

        # отправляем письмо
        # send_mail(
        #     subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',
        #     # имя клиента и дата записи будут в теме для удобства
        #     message=appointment.message,  # сообщение с кратким описанием проблемы
        #     from_email='peterbadson@yandex.ru',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        #     recipient_list=[]  # здесь список получателей. Например, секретарь, сам врач и т. д.
        # )
