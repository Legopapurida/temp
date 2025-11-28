from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('category/<slug:category_slug>/', views.GamesByCategoryView.as_view(), name='games_by_category'),
    path('tag/<slug:tag_slug>/', views.GamesByTagView.as_view(), name='games_by_tag'),
]