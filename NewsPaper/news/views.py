from datetime import datetime

from django.views import View
from django.shortcuts import render
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView
from django.core.paginator import Paginator

from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm


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

        if form.is_valid():
            form.save()

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

class NewsCreateView(CreateView):
    template_name = 'news/news_create.html'
    form_class = PostForm

class NewsUpdateView(UpdateView):
    template_name = 'news/news_create.html'
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

class NewsDeleteView(DeleteView):
    template_name = 'news/news_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'