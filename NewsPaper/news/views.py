from datetime import datetime

from django.views.generic import ListView, DetailView
from .models import Post

class NewsList(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'newslist'
    queryset = Post.objects.order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()  # добавим переменную текущей даты time_now
        return context

class NewsDetails(DetailView):
    model = Post
    template_name = 'news/news.html'
    context_object_name = 'news'
