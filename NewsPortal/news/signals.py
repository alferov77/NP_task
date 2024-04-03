from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives

from .models import Post, Subscriber

@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers(sender, instance, action, **kwargs):
    if action == 'post_add':
        recipient_list = Subscriber.objects.filter(
            category__in=instance.categories.all()
        ).values_list('user__email', flat=True).distinct()

        subject = f'Новая публикация в категории!'
        text_content = f'{instance.title}\nПодробнее: http://127.0.0.1:8000{instance.get_absolute_url()}'
        html_content = f'<p><strong>{instance.title}</strong></p><p>Подробнее: <a href="http://127.0.0.1:8000{instance.get_absolute_url()}">ссылка на статью</a></p>'

        for email in recipient_list:
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
