from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from .filters import NewsFilter
from .forms import PostForm
from .models import Post

from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.views.decorators.csrf import csrf_protect
from .models import Subscriber, Category



class NewsListView(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(post_type='NW').order_by('-creation_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context

class NewsDetailView(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news'

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    raise_exception = True
    form_class = PostForm
    template_name = 'news/post_form.html'

    def form_valid(self, form):
        form.instance.post_type = 'NW' if 'news' in self.request.path else 'AR'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news_list')

class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'news/post_form.html'

    def form_valid(self, form):
        form.instance.post_type = 'NW' if 'news' in self.request.path else 'AR'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news_detail', kwargs={'pk': self.object.pk})

class PostDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news/post_confirm_delete.html'
    success_url = reverse_lazy('news_list')


def search_news(request):
    news_list = Post.objects.all()
    news_filter = NewsFilter(request.GET, queryset=news_list)
    return render(request, 'news/search_news.html', {'filter': news_filter})

@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscriber.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscriber.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscriber.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )