from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('posts/', views.PostListView.as_view(), name='posts'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
]