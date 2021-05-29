from django_filters import FilterSet
from .models import Post


# создаём фильтр
class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields =  {'created': ['gt'],
                   'title': ['icontains'],
                   'author__user__username': ['icontains']
                   }