import atexit
from django.utils import timezone
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from .models import Post, Subscriber


def send_weekly_newsletter():
    one_week_ago = timezone.now() - timezone.timedelta(weeks=1)
    messages = []
    for subscriber in Subscriber.objects.all():
        posts = Post.objects.filter(
            categories__subscriptions=subscriber,
            creation_date__gte=one_week_ago
        ).distinct()

        if posts:
            subject = f'Новости за неделю в категории {subscriber.category.name}!'
            html_content = render_to_string(
                'news/weekly_newsletter.html',
                {'posts': posts, 'category': subscriber.category}
            )
            message = ('', html_content, None, [subscriber.user.email])
            messages.append(message)

    send_mass_mail(messages, fail_silently=False)


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

scheduler.add_job(
    send_weekly_newsletter,
    trigger='cron',
    day_of_week='fri',
    hour=18,
    minute=0,
    id='send_weekly_newsletter',
    max_instances=1,
    replace_existing=True,
)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
