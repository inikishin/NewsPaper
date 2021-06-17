from django.urls import path

from .views import NewsList, NewsDetails, NewsSearch, NewsCreateView, NewsUpdateView, NewsDeleteView, category_view, subscribe

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetails.as_view()),
    path('category/<int:pk>', category_view),
    path('category/subscribe/', subscribe, name = 'subscribe'),
    path('search/', NewsSearch.as_view()),
    path('create/', NewsCreateView.as_view(), name='news_create'),
    path('create/<int:pk>', NewsUpdateView.as_view(), name='news_update'),
    path('delete/<int:pk>', NewsDeleteView.as_view(), name='news_delete'),
]

