from celery import shared_task
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_managers, send_mail
from .models import Post
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from news.models import PostCategory
from django.template.loader import render_to_string
from allauth.account.signals import user_signed_up
from django.utils import timezone
import time
from NewsPaper.settings import DEFAULT_FROM_EMAIL

from datetime import datetime
from .models import *

@shared_task
def send_notifications(preview, pk, title, subscribers):
    html_content = render_to_string(
        'email_post_created.html',
        {
            'text':preview,
            'link': f'{settings.SITE_URL}/news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject = title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.postCategory.all()
        subscribers: list[str]=[]
        for category in categories:
            subscribers += category.subscribers.all()

        subscribers = [s.email for s in subscribers]

        send_notifications(instance.preview(), instance.pk, instance.title, subscribers)

@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")


@shared_task
def notify_weekly():
    today = datetime.datetime.now()
    last_week=today-datetime.timedelta(days=7)
    posts = Post.objects.filter(dateCreation__gte=last_week)
    print(posts)
    categories = set(posts.values_list('postCategory__name', flat=True))
    print(categories)
    subscribers = set(Category.objects.filter(name__in=categories).values_list("subscribers__email", flat=True))
    print(subscribers)
    html_content = render_to_string(
        'daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )
    print(html_content)
    msg = EmailMultiAlternatives(
        subject="Posts on week",
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()