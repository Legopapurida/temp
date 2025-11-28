from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from .models import Post, UserProfile


class PostListView(ListView):
    model = Post
    template_name = 'community/posts.html'
    context_object_name = 'posts'
    paginate_by = 20


class ProfileView(DetailView):
    model = User
    template_name = 'community/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        try:
            context['profile'] = user.userprofile
        except UserProfile.DoesNotExist:
            context['profile'] = None
        context['user_posts'] = Post.objects.filter(author=user)[:10]
        return context