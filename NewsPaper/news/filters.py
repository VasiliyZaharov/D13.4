from django_filters import FilterSet, DateTimeFilter
from django.forms import DateTimeInput
from .models import Post
import logging

class ErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR


class PostFilter(FilterSet):
    added_after = DateTimeFilter(
        field_name='dateCreation',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'categoryType': ['icontains']
        }