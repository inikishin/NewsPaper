from django.urls import path

from .views import NewsList, NewsDetails

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetails.as_view()),
]

